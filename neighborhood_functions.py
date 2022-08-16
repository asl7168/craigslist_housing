import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import json
import csv
import re
import geoplot as gplt
from shapely.geometry import Point

from demographics_multistate import get_demographics, demographics_by_tract
from GIS_data/state_codes import state_codes

fieldnames = ['post_id', 'title', 'price', 'neighborhood', 'map_address', 'street_address', 'latitude', 'longitude', 'data_accuracy', 'posted', 'updated', 'available', 'housing_type', 'bedrooms', 'bathrooms', 'laundry', 'parking', 'sqft', 'flooring', 'rent_period', 'app_fee', 'broker_fee', 'cats_ok', 'dogs_ok', 'no_smoking', 'furnished', 'wheelchair_access', 'AC', 'EV_charging', 'posting_body', 'images', 'url','mention','neighborhood_id']

#generate average statistics for census tracts of each gentrification typology
#results are printed to the console
def stats_by_gentrification_status(metro_area):
    states = state_codes[metro_area]
    data = demographics_by_tract(metro_area, states)
    #data = get_demographics(metro_area,states)
    typologies = ['Advanced Gentrification', 'At Risk of Becoming Exclusive', 'At Risk of Gentrification', 'Becoming Exclusive', 'Early/Ongoing Gentrification', 'High Student Population',
                  'Low-Income/Susceptible to Displacement', 'Ongoing Displacement', 'Stable Moderate/Mixed Income', 'Advanced Exclusive', 'Unavailable or Unreliable Data', 'Stable/Advanced Exclusive', 'None']
    new = {}
    old = {}
    for t in typologies:
        new[t] = defaultdict(float)
        old[t] = defaultdict(float)
    print("here")
    for key in data:
        i = data[key]
        if i != None and i['white'] != 'NA' and i['white_old'] != 'NA':
            t = i['typology']
            new[t]['count'] += 1
            new[t]['white'] += i['white']
            new[t]['black'] += i['black']
            new[t]['asian'] += i['asian']
            new[t]['latinx'] += i['latinx']
            new[t]['below25k'] += i['below25k']
            new[t]['college'] += i['college']
            new[t]['foreignborn'] += i['foreignborn']
            new[t]['renteroccupied'] += i['renteroccupied']
            new[t]['last10yrs'] += i['last10yrs']
            new[t]['vacancy'] += i['vacancy']
            new[t]['professional'] += i['professional']
            new[t]['new_residents'] += i['new_residents']
            new[t]['non_english'] += i['non_english']

            if i['median_income'] > 0:
                new[t]['median_income'] += i['median_income']
            else:
                new[t]['median_income'] += new[t]['median_income']/new[t]['count']

            if i['travel_time'] > 0:
                new[t]['travel_time'] += i['travel_time']
            else:
                new[t]['travel_time'] += new[t]['travel_time']/new[t]['count']

            if i['avg_rent'] > 0:
                new[t]['avg_rent'] += i['avg_rent']
            else:
                new[t]['avg_rent'] += new[t]['avg_rent']/new[t]['count']

            old[t]['count'] += 1
            old[t]['white'] += i['white_old']
            old[t]['black'] += i['black_old']
            old[t]['asian'] += i['asian_old']
            old[t]['latinx'] += i['latinx_old']
            old[t]['below25k'] += i['below25k_old']
            old[t]['college'] += i['college_old']
            old[t]['foreignborn'] += i['foreignborn_old']
            old[t]['renteroccupied'] += i['renteroccupied_old']
            old[t]['last10yrs'] += i['last10yrs_old']
            old[t]['vacancy'] += i['vacancy_old']
            old[t]['professional'] += i['professional_old']
            old[t]['new_residents'] += i['new_residents_old']
            old[t]['non_english'] += i['non_english_old']
            if i['median_income_old'] > 0:
                old[t]['median_income'] += i['median_income_old']
            else:
                old[t]['median_income'] += old[t]['median_income']/old[t]['count']
            if i['travel_time_old'] > 0:
                old[t]['travel_time'] += i['travel_time_old']
            else:
                old[t]['travel_time'] += old[t]['travel_time']/old[t]['count']
            if i['avg_rent_old'] > 0:
                old[t]['avg_rent'] += i['avg_rent_old']
            else:
                old[t]['avg_rent'] += old[t]['avg_rent']/old[t]['count']

    for t in typologies:
        print(t)
        for key in new[t]:
            if key == 'count':
                print(key, new[t][key])
            else:
                result = (new[t][key]-old[t][key]) / \
                    old[t][key] if old[t][key] != 0 else 0
                print(key, result)
    for t in typologies:
        print(t)
        for key in new[t]:
            if key == 'count':
                print(key, new[t][key])
            else:
                print(key, new[t][key]/new[t]['count'])

    for t in typologies:
        print(t)
        for key in new[t]:
            if key == 'count':
                print(key, new[t][key])
            else:
                print(key, new[t][key]/new[t]['count'] -
                      old[t][key]/old[t]['count'])


#generate csv of all posts that mention NEIGHBORHOOD
def filter_rows(path, neighborhood):
    rows = []
    
    with open(path, newline='') as csvfile:
         reader = csv.DictReader(csvfile)
         for row in reader:
           if row['posting_body'].find(neighborhood)>-1:
             rows.append(row)
    
    with open('csv/temp.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in rows:
            writer.writerow(row)

#generate heatmap of posts mentioning NEIGHBORHOOD
def get_heatmap(csv_path, shp_path, neighborhood):
    filter_rows(csv_path, neighborhood)
    ads_csv = pd.read_csv('csv/temp.csv')
    print(neighborhood+str(len(ads_csv)))
    if len(ads_csv)>4:
        geometry = ads_csv.apply(lambda row: Point(row.longitude,row.latitude), axis=1)
        ads = gpd.GeoDataFrame(ads_csv, geometry=geometry)
        chicago = gpd.read_file(shp_path)
        
        city = gplt.polyplot(chicago)
        gplt.kdeplot(ads, cmap='Reds', ax=city, extent = (-87.946,41.64,-87.52,42.03))
        title = re.sub(r'[^a-zA-Z]','',neighborhood)
        print(title)
        plt.savefig("./heatmaps/"+title+str(len(ads_csv))+".png")
        plt.close()
    
#generate heatmaps for every neighborhood in Chicago
def generate_chicago():
    with open('csv/chicago_neighborhood_names.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            get_heatmap('csv/CL_housing.csv','GIS_data/chicago_neighborhoods.shp',row['PRI_NEIGH'])

#add GIS neighborhood classification to posts
def add_neighborhood():
    ads = []
    neighborhoods = []
    name_dict = {}
    len_dict = {}
    
    with open('csv/CL_housing.csv', newline='') as csvfile:
         reader = csv.DictReader(csvfile)
         for row in reader:
             ads.append(row)
             
    with open('csv/Neighborhoods_2012b.csv', newline='') as csvfile:
         reader = csv.DictReader(csvfile)
         for row in reader:
             neighborhoods.append(row['PRI_NEIGH'])
             neighborhoods.append(row['SEC_NEIGH'])
             name_dict[row['PRI_NEIGH']] = row['PRI_NEIGH']
             name_dict[row['SEC_NEIGH']] = row['PRI_NEIGH']
             len_dict[row['PRI_NEIGH']] = row['SHAPE_LEN']
    
    for ad in ads:
        ad['mention'] = None
        index = len(ad['posting_body'])
        ad['neighborhood_id']=None
        for n in neighborhoods:
            i = ad['posting_body'].lower().find(n.lower())
            if i>-1 and i<index:
                ad['mention']=name_dict[n]
                ad['neighborhood_id'] = len_dict[name_dict[n]]
                
    with open('csv/CL_housing_with_mentions.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for ad in ads:
            writer.writerow(ad)

