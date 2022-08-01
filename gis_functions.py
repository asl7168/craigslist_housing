import csv

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
    # these were generated from the dictionary keys at the end of all this code and just copied up here
    fieldnames = ['post_id', 'title', 'price', 'neighborhood', 'map_address', 'street_address', 'latitude', 'longitude', 'data_accuracy', 'posted', 'updated', 'available', 'housing_type', 'bedrooms', 'bathrooms', 'laundry', 'parking', 'sqft', 'flooring', 'rent_period', 'app_fee', 'broker_fee', 'cats_ok', 'dogs_ok', 'no_smoking', 'furnished', 'wheelchair_access', 'AC', 'EV_charging', 'posting_body', 'images', 'url','mention','neighborhood_id']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    
    for ad in ads:
        writer.writerow(ad)
