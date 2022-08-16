import csv

neighborhoods = []
data = []
output = []

with open('ads_with_neighborhoods.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        data.append(row)

with open('Neighborhoods_2012b.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        neighborhoods.append(row['PRI_NEIGH'])


for n in neighborhoods:
    row = {'name': n, 'self': 0, 'other': 0, 'referrals': 0,
           'rent': 0, 'freq': 0, 'ref_ratio': 0, 'references': 0}
    count = 0
    internal_references = 0
    for d in data:
        if d['pri_neigh'] == n:
            row['freq'] += 1
            if d['price'] != '<Null>':
                count += 1
                row['rent'] += int(d['price'])
            if d['mention'] == n:
                row['self'] += 1
            else:
                row['other'] += 1
        elif d['mention'] == n:
            row['referrals'] += 1
        if d['posting_body'].lower().find(n.lower()) > -1:
            row['references'] += 1
            if d['pri_neigh'] == n:
                internal_references += 1
    if count > 0:
        row['rent'] = row['rent']/count
    if row['references'] > 0:
        row['ref_ratio'] = internal_references/row['references']
    output.append(row)

print(output)

with open('calculations.csv', 'w', newline='', encoding='utf-8') as csvfile:
    # these were generated from the dictionary keys at the end of all this code and just copied up here
    fieldnames = ['name', 'self', 'other', 'referrals',
                  'rent', 'freq', 'references', 'ref_ratio']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for row in output:
        writer.writerow(row)
