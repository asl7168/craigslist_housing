from bs4 import BeautifulSoup
import re
import os
import json
import spacy
import pandas as pd
from html import unescape
from tqdm import tqdm

# new comment
def find_strings(keywords, search_list):
    """ Searches for strings in a list and returns matches. This will be used to find 
    certain posting details from an aggregated list of options that users have when they create the post.
    Some are required like laundry and parking. Others are optional like flooring type, rent period, 
    pet info, AC, etc. 

    Parameters 
    ----------
    keywords : list
        A list of strings to search for

    search_list : list
        A list of strings to search in 


    Returns
    -------
    str
        Either the full string from the list or "NA" if doesn't exisit  
    """
    match = [item for item in search_list for keyword in keywords if keyword in item] 
    
    if len(match) == 0:
        return "NA"
    elif len(match) == 1:
        return match[0]
    else:
        return match


def clean_if_exists(s):
    """ For some posting details such as rent period, app fee, flooring etc., we only need the
    info to the right of the ':'. This function checks if this info is included in post (i.e. not "NA")
    and if so, splits and cleans it.

    Parameters
    ----------
    s : str
        The string to check and clean

    Returns
    -------
    str
        Either "NA" if input string is "NA" or split/stripped string 
    """
    
    if s != 'NA':
        if not isinstance(s,str):
            s = s[0]
        output = s.split(':')[1].strip()
        return output
    else:
        return s


def yes_if_exists(s):
    """ For some posting details, such as pets, no smoking, furnished, if they aren't explicitly marked, 
    it doesn't neccessarily mean that's not true for the property. This function checks for the existence 
    of these details (checkbox options when making post) and assigns 'yes' if exists and 'NA' if not.

    Parameters
    ----------
    s : str
        The string to check

    Returns
    -------
    str
        Either 'NA' if input string is 'NA' or 'yes'
    """
    if s != 'NA':
        return True
    else:
        return s


def process_html(directory):
    """ Processes every HTML file from the given directory to individual JSON files (default)

    Parameters
    ----------
        directory (string): filepath to directory of HTML files
    """
    city = directory.split("/")[-1]  # assumes directory name of form cityname_html (e.g. "chicago_html", "newyork_html")
    nlp = spacy.load("en_core_web_sm")  # python -m spacy download en_core_web_sm

    if not os.path.exists(f"./json/{city}"): os.makedirs(f"./json/{city}")
    
    for filename in tqdm(os.listdir(directory), desc=f"Processing html from {directory}..."):
        filepath = os.path.join(directory, filename)
        
        if not os.path.isfile(filepath): continue

        # open html and create soup
        with open(filepath, encoding='utf-8') as html_file:
            soup = BeautifulSoup(html_file, 'lxml')
        
        # get unique post ID
        try:
            post_id = int(soup.find(string=re.compile("post id")).split(':')[1].strip())
        except:
            continue
        
        posting_infos = soup.find('div', class_='postinginfos')  # posting/updating dates and times
        
        timing = posting_infos.find_all('time', class_='date timeago')
        datetime = [item.text for item in timing]
        posted = datetime[0]  # first item in list will be posting datetime
        updated = datetime[1] if len(datetime) > 1 else "NA"  # any additional datetimes will be updates

        # handle if a post is a repost
        repost_of_script = str(soup('script')[3])
        repost_of = re.search(r"repost_of: (\d+)", repost_of_script)
        repost_of = int(repost_of.group(1)) if repost_of else None
        
        if repost_of:
            json_path = f"./json/{city}/{repost_of}.json"
            if os.path.exists(json_path):  # if its file already exists, modify the repost_dates
                with open(json_path, "r") as json_file: data = json.load(json_file)
                data["repost_dates"] = data["repost_dates"].append(posted) if data["repost_dates"] else [posted]
                with open(json_path, "w") as json_file: json.dump(data, json_file, indent=1)
            else:  # otherwise, handle later (see L303, L314, L342)
                pass
        
        url = soup.find('link', rel='canonical').get('href')  # get post url
        
        # find posting title text which will include pricing, post title, and neighborhood (optional)
        title_text = soup.find('span', class_="postingtitletext")
        title = title_text.find('span', id='titletextonly')
        
        # find pricing info, extract text, strip whitespace, remove non-integer characters
        pricing_info = title_text.find('span', class_="price")
        if pricing_info:
            price = round(float(pricing_info.text.strip().replace("$", "").replace(",", "")))
        else:
            price = "NA"
        
        # if neighborhood is included (doesn't have to be), will be found here in the title text
        post_hood = title_text.find('small')
        neighborhood = post_hood.text.strip().strip('()') if post_hood else "NA"
        
        # get availability date
        # choose to grab the actual date instead of the text 'available jul 1' for example
        availability = soup.find(class_="housing_movein_now property_date shared-line-bubble")
        available = availability.get('data-date') if availability else "NA"
        
        # get map and address info
        mapbox = soup.find('div', class_='mapbox')
        if mapbox:
            latitude = float(mapbox.find(id='map').get('data-latitude'))
            longitude = float(mapbox.find(id='map').get('data-longitude'))
            
            # not sure exactly what data_accuracy means in this context, but it varies a lot by post
            data_accuracy = int(mapbox.find(id='map').get('data-accuracy'))
        
            # some posts just have street address, others include nearby cross streets formatted as
            # 'street address near street'. We account for both
            address = mapbox.find('div', class_="mapaddress")
            if address:
                map_address = address.text
            elif neighborhood[0].isdigit():
                map_address = neighborhood
            else:
                map_address = "NA"
            
            if "near" in map_address:
                street_address = map_address.split('near')[0]
            else:
                street_address = map_address
        else:
            latitude = longitude = data_accuracy = map_address = street_address = "NA"
        
        # get body of post
        posting_body = str(soup.find('section', id="postingbody"))
        posting_body = [unescape(text.replace("\n", "").replace("</section>", "")).strip() for text in re.split(r"<[^>]+>", 
                        posting_body)]
        posting_body = [text for text in posting_body if text != ""]
        docs = [nlp(s).sents for s in posting_body]  # do sentence segmentation on every string/item from the split body text
        sents = [str(sent) for doc in docs for sent in doc][1:]  # get every sentence from every doc in docs; [1:] to exclude "QR..." bit
        posting_body = [re.sub(r"(http|www)?[^\s]+\.(com|org|net)(\/[^\s]+)*", "<URL>", sent) for sent in sents]  # basic URL tokenization


        # get urls for images if post has them
        images = []
        imgList = soup.find('div', id='thumbs')
        if imgList:
            for tag in imgList.find_all('a'):
                img_url = tag.get('href')
                images.append(img_url)
        else:
            images = "NA"
        
        # this gets all the posting details that appear under the map. They look like tags, and are
        # the output of the user selecting specific options when they make the post. This gathers them in
        # a 'specifications' list which we can search through. There are two instances of the class "attrgroup",
        # the first is always just the bed/bath, sqft(if provided), and availability. The second has all
        # the other apt features.
        attrgroup = soup.find_all('p', class_="attrgroup")
        specs = [item.text for group in attrgroup for item in group.find_all("span")]
        # for group in attrgroup:
        #     for item in group.find_all("span"):
        #         specs.append(item.text)
        
        # required information:
        bedbath = find_strings(["BR"], specs)
        if bedbath != "NA": 
            bedbath_re = r"(\.?[0-9]+)+"
            
            if not isinstance(bedbath, str): bedbath = bedbath[0]
            
            bedbath = bedbath.split("/")
            bed = bedbath[0]
            bed = int(re.search(bedbath_re, bed).group())
            
            bath = bedbath[1]
            bath = re.search(bedbath_re, bath)
            
            if bath: 
                bath = float(bath.group())
            elif re.search(r"shared", bedbath[1]): 
                bath = "shared"
            elif re.search(r"split", bedbath[1]):
                bath = "split"

            bath = bath if bath else "NA"  # if there isn't an X.Y number of baths or
        else: 
            bed = bath = bedbath
        
        # all possible laundry options from drop down menu include either 'w/d' or 'laundry' so searching
        # for just those strings will return all possible matches
        laundry = find_strings(['w/d', 'laundry'], specs)
        # same for parking: there are a number of options but all accounted for by these 3 strings.
        parking = find_strings(['parking', 'garage', 'carport'], specs)
        
        # optional details
        # possble housing options
        housing_type = ['apartment', 'condo', 'cottage', 'duplex', 'flat', 'house',
                        'in-law', 'loft', 'townhouse', 'manufactured', 'assisted', 'land']
        housing = find_strings(housing_type, specs)
        if not isinstance(housing, str): housing = housing[0]
        
        sqft = find_strings(['ft2'], specs).replace('ft2','')
        if sqft != 'NA': sqft = int(sqft)
        
        # the group of features/specifications that are formatted name: details
        # use our clean up function to makes things easier
        flooring = clean_if_exists(find_strings(['flooring'], specs))
        rent_period = clean_if_exists(find_strings(['rent period'], specs))
        app_fee = find_strings(['application'], specs)
        app_fee = clean_if_exists(app_fee[0]) if isinstance(app_fee, list) else clean_if_exists(app_fee)
        broker_fee = clean_if_exists(find_strings(['broker'], specs))
        
        # the group of features that we just want to know if True or 'unspecified'
        cats_ok = yes_if_exists(find_strings(['cats'], specs))
        dogs_ok = yes_if_exists(find_strings(['dogs'], specs))
        no_smoking = yes_if_exists(find_strings(['smoking'], specs))
        furnished = yes_if_exists(find_strings(['furnished'], specs))
        wheelchair_access = yes_if_exists(find_strings(["wheelchair"], specs))
        AC = yes_if_exists(find_strings(['air'], specs))
        EV_charging = yes_if_exists(find_strings(['EV'], specs))
        
        # creating the dictionary
        post_details = {
            "post_id": post_id if not repost_of else repost_of,
            "title": title.text,
            "price": price,
            "neighborhood": neighborhood,
            "map_address": map_address,
            "street_address": street_address,
            "latitude": latitude,
            "longitude": longitude,
            "data_accuracy": data_accuracy,
            "posted": posted.strip(),
            "updated": updated.strip(),
            "repost_dates": [] if not repost_of else [posted],
            "available": available.strip(),
            "housing_type": housing,
            "bedrooms": bed,
            "bathrooms": bath,
            "laundry": laundry,
            "parking": parking,
            "sqft": sqft,
            "flooring": flooring,
            "rent_period": rent_period,
            "app_fee": app_fee,
            "broker_fee": broker_fee,
            "cats_ok": cats_ok,
            "dogs_ok": dogs_ok,
            "no_smoking": no_smoking,
            "furnished": furnished,
            "wheelchair_access": wheelchair_access,
            "AC": AC,
            "EV_charging": EV_charging,
            "posting_body": posting_body,
            "images": images,
            "url": url
        }
        
        json_obj = json.dumps(post_details, indent=1)
        json_path = f"./json/{city}/{repost_of}.json" if repost_of else f"json/{city}/{post_id}.json"

        with open(json_path, "w") as outfile:
            outfile.write(json_obj)


def jsons_to_csv(directory):
    result_df = pd.DataFrame(columns=["post_id", "title", "price", "neighborhood", "map_address", "street_address", 
                                      "latitude", "longitude", "data_accuracy", "posted", "updated", "repost_dates",
                                      "available", "housing_type", "bedrooms", "bathrooms", "laundry", "parking", "sqft",
                                      "flooring", "rent_period", "app_fee", "broker_fee", "cats_ok", "dogs_ok", "no_smoking",
                                      "furnished", "wheelchair_access", "AC", "EV_charging", "posting_body", "images", "url"])
    
    city = directory.split("/")[-1]
    
    if not os.path.exists(f"./json/{city}"): os.makedirs(f"./json/{city}")
    
    for filename in tqdm(os.listdir(directory), desc=f"Making csv from json in {directory}..."):
        json_path = f"{directory}/{filename}"
        with open(json_path, "r") as json_file: 
            data = json.load(json_file)
        
        df = pd.DataFrame([data], columns=data.keys())
        result_df = pd.concat([result_df, df])

    result_df.to_csv(f"./csv_dumps/{city}_csv_dump.csv", index=False)


if __name__ == '__main__':
    process_html("./html/chicago")
    jsons_to_csv("./json/chicago")
