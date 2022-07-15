import requests
import csv
import geopandas

#census variables: https://api.census.gov/data/2020/acs/acs5/profile/variables.html
#state codes: https://www.nlsinfo.org/content/cohorts/nlsy97/other-documentation/geocode-codebook-supplement/attachment-100-census-bureau


def get_data(state,county,tract):
    r = requests.get('https://api.census.gov/data/2020/acs/acs5/profile?get=DP05_0064PE,DP05_0065PE,DP05_0067PE,DP05_0071PE,DP03_0052PE,DP03_0053PE,DP03_0054PE,DP03_0062E&for=tract:'+tract+'&in=state:'+state+'%20county:'+county+'&key=901e1c41a36cd6bbee390e6cc013021757d66ffd')
    try:
        data = r.json()
    except requests.exceptions.JSONDecodeError:
        return {},{}
    if(len(data)<100):
      print(data)
    race = {}
    income = {}
    for items in data[1:]:
      
      name = items[8]+items[9]+items[10]
      if items[8]== '17' and items[9]=='031' and items[10]=='320100':
          print("A")
      race[name] = {
        'white': float(items[0]),
        'black': float(items[1]),
        'asian': float(items[2]),
        'latinx': float(items[3])
      }
      income[name] = {
        'poverty': float(items[4])+float(items[5])+float(items[6]),
        'median_income': float(items[7])
      }
    return race,income
      

def assign_categories(race,income):
    demographics = {}
    for i in race.keys():
        if income[i]['poverty'] > 30:
          poverty = 'poor'
        else:
          poverty = 'nonpoor'
        demographics[i] = {
          'race': max(race[i],key = race[i].get),
          'poverty': poverty
        }
    #print(demographics['17031320100'])
    return demographics

def remove_NA(read_path,write_path):    
    rows=[]
    data = {}
    with open(read_path) as csvfile:
       reader = csv.DictReader(csvfile)
       for row in reader:
         rows.append(row)
         data[str(row['post_id'])] = row
    
    
    with open(write_path,'w') as outfile:
        fieldnames = ["post_id", "title", "price", "neighborhood", "map_address", "street_address", "latitude", "longitude", "data_accuracy", "posted", "updated", "repost_dates", "available", "housing_type", "bedrooms", "bathrooms", "laundry", "parking", "sqft", "flooring", "rent_period", "app_fee", "broker_fee", "cats_ok", "dogs_ok", "no_smoking", "furnished", "wheelchair_access", "AC", "EV_charging", "posting_body", "images", "url"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in rows:
          if row['latitude'] != 'NA' and row['longitude'] !='NA':
            writer.writerow(row)
    return data

def get_geoid(csv_read_path,csv_write_path,map_path,with_typology=False):
    data = remove_NA(csv_read_path,csv_write_path)
    df = geopandas.read_file(csv_write_path)
    city_map = geopandas.read_file(map_path)
    geometry = geopandas.points_from_xy(df.longitude, df.latitude)
    ads = geopandas.GeoDataFrame(data = df,geometry = geometry)
    
    combined = ads.sjoin(city_map)
    
    for i in combined.index.values:
      post_id = str(combined.at[i,'post_id'])
      post_id = post_id.split('\n')[0].split(' ')
      if with_typology:
        typology = str(combined.at[i,'Typology'])
        typology = typology.split('\n')[0].split(' ')
      else:
        typology = 'NA'.split(' ')
      geoid = str(combined.at[i,'GEOID_dbl'])
      geoid = geoid.split('\n')[0].split(' ')
      if len(post_id)>1 and len(typology) > 1:
        post_id = post_id[4]
        typology = ' '.join(typology[4:])
        geoid = geoid[4]
      else:
        post_id = post_id[0]
        typology = ' '.join(typology)
        geoid = geoid[0]
      data[post_id]['typology'] = typology
      data[post_id]['GEOID'] = str(round(float(geoid)))
    return data

def add_fields(data,key,demographics,repeat = False):
    d = data[key]
    if d.get('GEOID') and demographics.get(d['GEOID']):
      poverty = demographics[d['GEOID']]['poverty']
      race = demographics[d['GEOID']]['race']
    elif d.get('GEOID') and not repeat:
      temp_race,temp_income = get_data(d['GEOID'][:2],d['GEOID'][2:5],d['GEOID'][5:])
      temp_demographics = assign_categories(temp_race,temp_income)
      poverty,race = add_fields(data,key,temp_demographics,repeat = True)
    else:
      poverty = 'NA'
      race = 'NA'
    return poverty,race
      
def get_demographics(metro_area,state):
  csv_read='csv_dumps/'+metro_area+'_csv_dump.csv'
  csv_write = 'csv_dumps/'+metro_area+'_filtered.csv'
  map_path = 'GIS_data/'+state+'/tl_2018_'+state+'_tract.shp'
  race,income = get_data(state,'*','*')
  demographics = assign_categories(race,income)
  data = get_geoid(csv_read,csv_write,map_path)
  
  for key in data:
      data[key]['poverty'],data[key]['race'] = add_fields(data,key,demographics)
  return data
  
  

#data = get_demographics('chicago','17')
