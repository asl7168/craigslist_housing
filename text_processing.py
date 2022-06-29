from bs4 import BeautifulSoup
import re
import os
import json

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
    match = []
    for item in search_list:
        for s in keywords:
            if s in item:
                match.append(item)
    
    if len(match) == 0:
        return "NA"
    elif len(match) == 1:
        return ''.join(match)
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


# open csv
# if os.path.exists("data/csv_dumps/CL_housing.json"): 
#    open_mode = "a"
# else: 
#   open_mode = "w"

# with open('data/csv_dumps/CL_housing.json', open_mode) as outfile:

# get file path for each html file in directory

directory = 'html/' # change this to whatever the directory of files is called
counter = 0
for idx, fname in enumerate(os.listdir(directory)):
    file_path = os.path.join(directory, fname)
    
    if idx % 100 == 0: print(idx)
    if not os.path.isfile(file_path): continue
    
    # open html and create soup
    with open(file_path, encoding='utf-8') as html_file:
        soup = BeautifulSoup(html_file, 'lxml')
    
    # get unique post ID
    try:
        post_id = soup.find(string=re.compile("post id")).split(':')[1].strip()
    except:
        continue
    
    # get post url
    url = soup.find('link', rel='canonical').get('href')
    
    # find posting title text which will include pricing, post title, and neighborhood (optional)
    title_text = soup.find('span', class_="postingtitletext")
    title = title_text.find('span', id='titletextonly')
    
    # find pricing info, extract text, strip whitespace, remove non-integer characters
    pricing_info = title_text.find('span', class_="price")
    if pricing_info:
        price = int(pricing_info.text.strip().replace(
            "$", "").replace(",", ""))
    else:
        price = "NA"
    
    # if neighborhood is included (doesn't have to be), will be found here in the title text
    post_hood = title_text.find('small')
    if post_hood:
        neighborhood = post_hood.text.strip().strip('()')
    else:
        neighborhood = "NA"
    
    # get availability date
    # I choose to grab the actual date instead of the text 'available jul 1' for example
    availability = soup.find(
        class_="housing_movein_now property_date shared-line-bubble")
    if availability:
        available = availability.get('data-date')
    else:
        available = "NA"
    
    # get map and address info
    mapbox = soup.find('div', class_='mapbox')
    if mapbox:
        latitude = float(mapbox.find(id='map').get('data-latitude'))
        longitude = float(mapbox.find(id='map').get('data-longitude'))
        # Not sure exactly what data_accuracy means in this context,
        # but it varies a lot by post, so may be useful later
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
    
    # posting/updating dates and times
    posting_infos = soup.find('div', class_='postinginfos')
    timing = posting_infos.find_all('time', class_='date timeago')
    datetime = []
    for item in timing:
        datetime.append(item.text)
    # first item in list will be posting datetime
    posted = datetime[0]
    # any additional datetimes will be updates
    if len(datetime) > 1:
        updated = datetime[1]
    else:
        updated = "NA"
    
    # get body of post
    posting_body = soup.find('section', id="postingbody")
    
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
    specs = []
    for group in attrgroup:
        for item in group.find_all("span"):
            specs.append(item.text)
    
    # required information:
    bedbath = find_strings(["BR"], specs)
    if bedbath != "NA": 
        bedbath_re = "(\.?[0-9]+)+"

        bedbath = bedbath.split("/")
        bed = bedbath[0]
        bed = int(re.search(bedbath_re, bed).group())
        # print(bed)
        bath = bedbath[1]
        bath = re.search(bedbath_re, bath)
        if bath: bath = float(bath.group())
        else: bath = re.search("share", bedbath[1])

        if bath: bath = 1.0
        else: bath = "NA"
    else: 
        bed = bath = bedbath
    
    # all possible laundry options from drop down menu include either 'w/d', or 'laundry' so searching
    # for just those strings will return all possible matches
    laundry = find_strings(['w/d', 'laundry'], specs)
    # same for parking: there are a number of options but all accounted for by these 3 strings.
    parking = find_strings(['parking', 'garage', 'carport'], specs)
    
    # optional details
    # possble housing options
    housing_type = ['apartment', 'condo', 'cottage', 'duplex', 'flat', 'house',
                    'in-law', 'loft', 'townhouse', 'manufactured', 'assisted', 'land']
    housing = find_strings(housing_type, specs)
    if not isinstance(housing, str):
      housing = housing[0]
    
    sqft = find_strings(['ft2'], specs).replace('ft2','')
    if sqft != 'NA':
      sqft = int(sqft)
    
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
        "post_id": int(post_id),
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
        "posting_body": posting_body.text.replace("\n", " "),
        "images": images,
        "url": url
    }
    
    json_obj = json.dumps(post_details, indent=1)
    
    with open("json/"+post_id+".json", "w") as outfile:
      outfile.write(json_obj)
