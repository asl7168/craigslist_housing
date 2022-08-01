import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import json
import csv
import re
import geoplot as gplt
from shapely.geometry import Point


def filter_rows(path, neighborhood):
    rows = []
    
    with open(path, newline='') as csvfile:
         reader = csv.DictReader(csvfile)
         for row in reader:
           if row['posting_body'].find(neighborhood)>-1:
             rows.append(row)
    
    with open('csv/temp.csv', 'w', newline='', encoding='utf-8') as csvfile:
        # these were generated from the dictionary keys at the end of all this code and just copied up here
        fieldnames = ['post_id', 'title', 'price', 'neighborhood', 'map_address', 'street_address', 'latitude', 'longitude', 'data_accuracy', 'posted', 'updated', 'available', 'housing_type', 'bedrooms', 'bathrooms', 'laundry', 'parking', 'sqft', 'flooring', 'rent_period', 'app_fee', 'broker_fee', 'cats_ok', 'dogs_ok', 'no_smoking', 'furnished', 'wheelchair_access', 'AC', 'EV_charging', 'posting_body', 'images', 'url','mention','neighborhood_id']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in rows:
            writer.writerow(row)


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
    
#filter_rows('csv/CL_housing.csv','Pullman')
#get_heatmap('csv/CL_housing.csv','GIS_data/chicago_neighborhoods.shp','Albany Park')
with open('csv/chicago_neighborhood_names.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        get_heatmap('csv/CL_housing.csv','GIS_data/chicago_neighborhoods.shp',row['PRI_NEIGH'])