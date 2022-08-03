import requests
import csv
import geopandas

#census variables: https://api.census.gov/data/2020/acs/acs5/profile/variables.html
#state codes: https://www.nlsinfo.org/content/cohorts/nlsy97/other-documentation/geocode-codebook-supplement/attachment-100-census-bureau
#maps source: https://www.census.gov/cgi-bin/geo/shapefiles/index.php?year=2018&layergroup=Census+Tracts


def get_data(state,county,tract):
    r_new = requests.get('https://api.census.gov/data/2020/acs/acs5/profile?get=DP05_0064PE,DP05_0065PE,DP05_0067PE,DP05_0071PE,DP03_0119PE,DP03_0062E,DP02_0068PE,DP02_0094PE,DP04_0047PE,DP04_0018PE,DP04_0017PE,DP04_0003PE,DP03_0027PE,DP03_0029PE,DP03_0025E,DP04_0052PE,DP04_0051PE,DP04_0134E,DP02_0114PE&for=tract:'+tract+'&in=state:'+state+'%20county:'+county+'&key=901e1c41a36cd6bbee390e6cc013021757d66ffd')
    try:
        data = r_new.json()
    except requests.exceptions.JSONDecodeError:
        return {},{},{},{}
    
    race,income,other = sort_into_objects(data,True)
    
    r_old = requests.get('https://api.census.gov/data/2010/acs/acs5/profile?get=DP05_0059PE,DP05_0060PE,DP05_0062PE,DP05_0066PE,DP03_0119PE,DP03_0062E,DP02_0067PE,DP02_0092PE,DP04_0046PE,DP04_0017PE,DP04_0018PE,DP04_0003PE,DP03_0027PE,DP03_0029PE,DP03_0025E,DP04_0050PE,DP04_0050PE,DP04_0132E,DP02_0112PE&for=tract:'+tract+'&in=state:'+state+'%20county:'+county+'&key=901e1c41a36cd6bbee390e6cc013021757d66ffd')
    try:
        data_old = r_old.json()
    except requests.exceptions.JSONDecodeError:
        return {},{},{},{}
    
    race_old,income_old,other_old = sort_into_objects(data_old,False) 
    
    race_diff={}
    total_income={}
    total_other={}
    for key in income.keys():
      if income.get(key,None) and income_old.get(key,None):
        race_diff[key]={
          'white_old': race_old[key]['white'],
          'black_old': race_old[key]['black'],
          'asian_old': race_old[key]['asian'],
          'latinx_old': race_old[key]['latinx']
        }
        total_income[key]= {
          'poverty': income[key]['poverty'],
          'median_income': income[key]['median_income'],
          'poverty_old': income_old[key]['poverty'],
          'median_income_old': 1.19*income_old[key]['median_income']
        }
        total_other[key]={
          'college': other[key]['college'],
          'foreignborn': other[key]['foreignborn'],
          'renteroccupied': other[key]['renteroccupied'],
          'last10yrs': other[key]['last10yrs'],
          'vacancy': other[key]['vacancy'],
          'college_old':other_old[key]['college'],
          'foreignborn_old':other_old[key]['foreignborn'],
          'renteroccupied_old':other_old[key]['renteroccupied'],
          'last10yrs_old':other_old[key]['last10yrs'],
          'vacancy_old': other_old[key]['vacancy'],
          'professional':other[key]['professional'],
          'professional_old':other_old[key]['professional'],
          'travel_time':other[key]['travel_time'],
          'travel_time_old':other_old[key]['travel_time'],
          'new_residents': other[key]['new_residents'],
          'avg_rent': other[key]['avg_rent'],
          'non_english': other[key]['non_english'],
          'new_residents_old': other_old[key]['new_residents'],
          'avg_rent_old': 1.19*other_old[key]['avg_rent'],
          'non_english_old': other_old[key]['non_english']
        }
      else:
        race_diff[key]={
          'white_old': 'NA',
          'black_old': 'NA',
          'asian_old': 'NA',
          'latinx_old': 'NA'
        }
        total_income[key]={
          'poverty': income[key]['poverty'],
          'median_income': income[key]['median_income'],
          'poverty_old': 'NA',
          'median_income_old': 'NA'
        }
        total_other[key]={
          'college': other[key]['college'],
          'foreignborn': other[key]['foreignborn'],
          'renteroccupied': other[key]['renteroccupied'],
          'last10yrs': other[key]['last10yrs'],
          'vacancy': other[key]['vacancy'],
          'college_old':'NA',
          'foreignborn_old':'NA',
          'renteroccupied_old':'NA',
          'last10yrs_old':'NA',
          'vacancy_old':'NA',
          'professional':other[key]['professional'],
          'professional_old':'NA',
          'travel_time':other[key]['travel_time'],
          'travel_time_old':'NA',
          'new_residents': other[key]['new_residents'],
          'avg_rent': other[key]['avg_rent'],
          'non_english': other[key]['non_english'],
          'new_residents_old': 'NA',
          'avg_rent_old': 'NA',
          'non_english_old': 'NA'
        }
    return race,total_income,total_other,race_diff

def sort_into_objects(data,is2020):
    race={}
    income={}
    other={}
    for items in data[1:]:
      
      name = items[19]+items[20]+items[21]
      race[name] = {
        'white': float(items[0]),
        'black': float(items[1]),
        'asian': float(items[2]),
        'latinx': float(items[3])
      }
      income[name] = {
        'poverty': float(items[4]),
        'median_income': float(items[5])
      }
      other[name] = {
        'college': float(items[6]),
        'foreignborn': float(items[7]),
        'renteroccupied': float(items[8]),
        'last10yrs': float(items[9])+float(items[10]),
        'vacancy': float(items[11]),
        'professional': float(items[12])+float(items[13]),
        'travel_time': float(items[14]),
        'new_residents': float(items[15])+float(items[16]) if is2020 else float(items[15]),
        'avg_rent': float(items[17]),
        'non_english': float(items[18])
      }
    return race,income,other
      

def assign_categories(race,income,other,race_diff):
    demographics = {}
    for i in race.keys():
        if income[i]['poverty'] > 30:
          poverty = 'poor'
        else:
          poverty = 'nonpoor'
        demographics[i] = {
          'white':race[i]['white'],
          'black':race[i]['black'],
          'asian':race[i]['asian'],
          'latinx':race[i]['latinx'],
          'race': max(race[i],key = race[i].get),
          'white_old':race_diff[i]['white_old'],
          'black_old':race_diff[i]['black_old'],
          'asian_old':race_diff[i]['asian_old'],
          'latinx_old':race_diff[i]['latinx_old'],
          'below25k':income[i]['poverty'],
          'median_income':income[i]['median_income'],
          'below25k_old':income[i]['poverty_old'],
          'median_income_old':income[i]['median_income_old'],
          'poverty': poverty,
          'college': other[i]['college'],
          'foreignborn':other[i]['foreignborn'],
          'renteroccupied':other[i]['renteroccupied'],
          'last10yrs':other[i]['last10yrs'],
          'vacancy':other[i]['vacancy'],
          'college_old': other[i]['college_old'],
          'foreignborn_old':other[i]['foreignborn_old'],
          'renteroccupied_old':other[i]['renteroccupied_old'],
          'last10yrs_old':other[i]['last10yrs_old'],
          'vacancy_old':other[i]['vacancy_old'],
          'professional':other[i]['professional'],
          'professional_old':other[i]['professional_old'],
          'travel_time':other[i]['travel_time'],
          'travel_time_old':other[i]['travel_time_old'],
          'new_residents': other[i]['new_residents'],
          'avg_rent': other[i]['avg_rent'],
          'non_english': other[i]['non_english'],
          'new_residents_old': other[i]['new_residents_old'],
          'avg_rent_old': other[i]['avg_rent_old'],
          'non_english_old': other[i]['non_english_old']
        }
    return demographics

def remove_NA(read_path,write_path):    
    rows=[]
    data = {}
    with open(read_path) as csvfile:
       reader = csv.DictReader(csvfile)
       for row in reader:
         rows.append(row)
         data[str(row['post_id'])] = row
    
    count = 0
    with open(write_path,'w') as outfile:
        fieldnames = ["post_id", "title", "price", "neighborhood", "map_address", "street_address", "latitude", "longitude", "data_accuracy", "posted", "updated", "repost_dates", "available", "housing_type", "bedrooms", "bathrooms", "laundry", "parking", "sqft", "flooring", "rent_period", "app_fee", "broker_fee", "cats_ok", "dogs_ok", "no_smoking", "furnished", "wheelchair_access", "AC", "EV_charging", "posting_body", "images", "url"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in rows:
          if row['latitude'] != 'NA' and row['longitude'] !='NA':
            count +=1
            writer.writerow(row)
    return data

def get_geoid(csv_read_path,csv_write_path,states):

    data = remove_NA(csv_read_path,csv_write_path)
    df = geopandas.read_file(csv_write_path)
    geometry = geopandas.points_from_xy(df.longitude, df.latitude,crs = 'EPSG:4269')
    ads = geopandas.GeoDataFrame(data = df,geometry = geometry)
    
    for state in states:
      with_typology = state in ['13','17','08','06','53']
    
      map_path = 'GIS_data/'+state+'/tl_2018_'+state+'_tract.shp'
      city_map = geopandas.read_file(map_path)
      
      combined = geopandas.sjoin(ads,city_map)
      
      for i in combined.index.values:
        post_id = str(combined.at[i,'post_id'])
        post_id = post_id.split('\n')[0].split(' ')
        if with_typology:
          typology = str(combined.at[i,'Typology'])
          typology = typology.split('\n')[0].split(' ')
        else:
          typology = 'NA'.split(' ')
        geoid = str(combined.at[i,'GEOID'])
        geoid = geoid.split('\n')[0].split(' ')
        if len(post_id)>1:
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
      d['poverty'] = demographics[d['GEOID']]['poverty']
      d['race'] = demographics[d['GEOID']]['race']
      d['white'] = demographics[d['GEOID']]['white']
      d['black'] = demographics[d['GEOID']]['black']
      d['asian'] = demographics[d['GEOID']]['asian']
      d['latinx'] = demographics[d['GEOID']]['latinx']
      d['below25k'] = demographics[d['GEOID']]['below25k']
      d['median_income'] = demographics[d['GEOID']]['median_income']
      d['college'] = demographics[d['GEOID']]['college']
      d['foreignborn'] = demographics[d['GEOID']]['foreignborn']
      d['renteroccupied'] = demographics[d['GEOID']]['renteroccupied']
      d['last10yrs'] = demographics[d['GEOID']]['last10yrs']
      d['vacancy'] = demographics[d['GEOID']]['vacancy']
      d['white_old'] = demographics[d['GEOID']]['white_old']
      d['black_old'] = demographics[d['GEOID']]['black_old']
      d['asian_old'] = demographics[d['GEOID']]['asian_old']
      d['latinx_old'] = demographics[d['GEOID']]['latinx_old']
      d['below25k_old'] = demographics[d['GEOID']]['below25k_old']
      d['median_income_old'] = demographics[d['GEOID']]['median_income_old']
      d['college_old'] = demographics[d['GEOID']]['college_old']
      d['foreignborn_old'] = demographics[d['GEOID']]['foreignborn_old']
      d['renteroccupied_old'] = demographics[d['GEOID']]['renteroccupied_old']
      d['last10yrs_old'] = demographics[d['GEOID']]['last10yrs_old']
      d['vacancy_old'] = demographics[d['GEOID']]['vacancy_old']
      d['professional'] = demographics[d['GEOID']]['professional']
      d['professional_old'] = demographics[d['GEOID']]['professional_old']
      d['travel_time'] = demographics[d['GEOID']]['travel_time']
      d['travel_time_old'] = demographics[d['GEOID']]['travel_time_old']
      d['new_residents'] = demographics[d['GEOID']]['new_residents']
      d['new_residents_old'] = demographics[d['GEOID']]['new_residents_old']
      d['non_english'] = demographics[d['GEOID']]['non_english']
      d['non_english_old'] = demographics[d['GEOID']]['non_english_old']
      d['avg_rent'] = demographics[d['GEOID']]['avg_rent']
      d['avg_rent_old'] = demographics[d['GEOID']]['avg_rent_old']
    elif d.get('GEOID') and not repeat:
      temp_race,temp_income,temp_other,temp_race_diff = get_data(d['GEOID'][:2],d['GEOID'][2:5],d['GEOID'][5:])
      temp_demographics = assign_categories(temp_race,temp_income,temp_other,temp_race_diff)
      d = add_fields(data,key,temp_demographics,repeat = True)
    else:
      d['poverty'] = 'NA'
      d['race'] = 'NA'
      d['white'] = 'NA'
      d['black'] = 'NA'
      d['asian'] = 'NA'
      d['latinx'] = 'NA'
      d['below25k'] = 'NA'
      d['median_income'] = 'NA'
      d['college'] = 'NA'
      d['foreignborn'] = 'NA'
      d['renteroccupied'] = 'NA'
      d['last10yrs'] = 'NA'
      d['vacancy'] = 'NA'
      d['white_old'] = 'NA'
      d['black_old'] = 'NA'
      d['asian_old'] = 'NA'
      d['latinx_old'] = 'NA'
      d['below25k_old'] = 'NA'
      d['median_income_old'] = 'NA'
      d['college_old'] = 'NA'
      d['foreignborn_old'] = 'NA'
      d['renteroccupied_old'] = 'NA'
      d['last10yrs_old'] = 'NA'
      d['vacancy_old'] = 'NA'
      d['professional'] = 'NA'
      d['professional_old'] = 'NA'
      d['travel_time'] = 'NA'
      d['travel_time_old'] = 'NA'
      d['new_residents'] = 'NA'
      d['new_residents_old'] = 'NA'
      d['non_english'] = 'NA'
      d['non_english_old'] = 'NA'
      d['avg_rent'] ='NA'
      d['avg_rent_old'] = 'NA'
    return d
    
def demographics_by_tract(metro_area,states):
  tracts = {}
  data = {}
  with open ('./GIS_data/displacement-typologies/data/downloads_for_public/'+metro_area+".csv") as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
      tracts[row['GEOID']] = {'typology': row['Typology']}
  for state in states:
    race,income,other,race_diff = get_data(state,'*','*')
    data = assign_categories(race,income,other,race_diff)
  for key in tracts:
      #print(data)
      obj = data.get(key,None)
      if obj != None:
          obj['typology'] = tracts[key]['typology']
      tracts[key] = obj
  return tracts
      
    
      
      
def get_demographics(metro_area,states):
  csv_read='csv_dumps/'+metro_area+'_csv_dump.csv'
  csv_write = 'csv_dumps/'+metro_area+'_filtered.csv'
  demographics={}
  for state in states:
    race,income,other,race_diff = get_data(state,'*','*')
    demographics_state = assign_categories(race,income,other,race_diff)
    demographics.update(demographics_state)
  data = get_geoid(csv_read,csv_write,states)
  
  for key in data:
      data[key] = add_fields(data,key,demographics)
  return data
  
  

#data = get_demographics('chicago',['17'])
