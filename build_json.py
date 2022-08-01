from text_processing import process_html,jsons_to_csv 
from demographics_multistate import get_demographics 
from state_codes import state_codes
import json
import os
import csv
from collections import defaultdict

#state codes: https://www.nlsinfo.org/content/cohorts/nlsy97/other-documentation/geocode-codebook-supplement/attachment-100-census-bureau

def metro_area_data(metro_area):
  #process_html("./html/"+metro_area)
  #jsons_to_csv("./json/"+metro_area)
  states = state_codes[metro_area]
  data = get_demographics(metro_area,states)
  #print(data['3790493246'])
  
  #if not os.path.exists(f"./json_complete/{metro_area}"): os.makedirs(f"./json_complete/{metro_area}")
  
  #for key in data:
      #json_obj = json.dumps(data[key], indent=1)
      #json_path = f"./json_complete/{metro_area}/{key}.json"

      #with open(json_path, "w") as outfile:
      #    outfile.write(json_obj)
  with open(f'./csv_dumps/{metro_area}_complete.csv','w') as csvfile:
      fieldnames = ['documents','poverty','race','class','is_white']
      writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
      writer.writeheader()
      
      for key in data:
          item = data[key]
          orig_doc = item['posting_body']
          orig_doc.replace("[\'",'').replace("\']",'')
          doc = orig_doc.split('\', \'')
          race = item['race'] if item['race'] != 'white' else 'aawhite'
          obj = {
            'documents': ' '.join(doc[1:]),
            'poverty': item['poverty'],
            'race': race,
            'class': item['poverty']+"_"+race,
            'is_white': 'white' if item['race']=='white' else 'nonwhite',
            'college': item['college'],
            'foreignborn': item['foreignborn'],
            'renteroccupied': item['renteroccupied'],
            'after2010': item['after2010'],
            'vacancy': item['vacancy'],
            'rent': 'NA' if item['price']=='NA' else float(item['price'])/1000
          }
          if item['poverty'] != 'NA' and obj['rent'] != 'NA' and obj['rent']<=10:
            writer.writerow(obj)

def testing(metro_area):
    states = state_codes[metro_area]
    data = get_demographics(metro_area,states)
    typologies = ['Advanced Gentrification','At Risk of Becoming Exclusive','At Risk of Gentrification','Becoming Exclusive','Early/Ongoing Gentrification','High Student Population','Low-Income/Susceptible to Displacement','Ongoing Displacement','Stable Moderate/Mixed Income','Advanced Exclusive','Unavailable or Unreliable Data','Stable/Advanced Exclusive','None']
    totals = {}
    baseline={}
    for t in typologies:
      totals[t] = defaultdict(float)
      baseline[t] = defaultdict(float)
    print("here")
    for key in data:
      i = data[key]
      if i['white']!='NA' and i['white_diff']!='NA':
        t = i['typology']
        totals[t]['count'] += 1
        totals[t]['white_diff'] += i['white_diff']
        totals[t]['black_diff'] += i['black_diff']
        totals[t]['asian_diff'] += i['asian_diff']
        totals[t]['latinx_diff'] += i['latinx_diff']
        totals[t]['below25k_diff'] += i['below25k_diff']
        if i['median_income_diff'] > -1000000 and i['median_income_diff'] < 1000000:
          totals[t]['median_income_diff'] += i['median_income_diff']
        else:
          totals[t]['median_income_diff'] += totals[t]['median_income_diff']/totals[t]['count']
          
        if i['travel_time_diff'] > -10000 and i['travel_time_diff'] < 10000:
          totals[t]['travel_time_diff'] += i['travel_time_diff']
        else:
          totals[t]['travel_time_diff'] += totals[t]['travel_time_diff']/totals[t]['count']
          
        if i['avg_rent_diff'] > -10000 and i['avg_rent_diff'] < 10000:
          totals[t]['avg_rent_diff'] += i['avg_rent_diff']
        else:
          totals[t]['avg_rent_diff'] += totals[t]['avg_rent_diff']/totals[t]['count']
          #print("wrong",t,totals[t]['rent_burdened_diff'])
          
        totals[t]['college_diff'] += i['college_diff']
        totals[t]['foreignborn_diff'] += i['foreignborn_diff']
        totals[t]['renteroccupied_diff'] += i['renteroccupied_diff']      
        totals[t]['last10yrs_diff'] += i['last10yrs_diff'] 
        totals[t]['vacancy_diff'] += i['vacancy_diff']  
        totals[t]['professional_diff'] += i['professional_diff'] 
        totals[t]['new_residents_diff'] += i['new_residents_diff']
        totals[t]['non_english_diff'] += i['non_english_diff']

        
        
        baseline[t]['count'] += 1
        baseline[t]['white_diff'] += i['white_old']
        baseline[t]['black_diff'] += i['black_old']
        baseline[t]['asian_diff'] += i['asian_old']
        baseline[t]['latinx_diff'] += i['latinx_old']
        baseline[t]['below25k_diff'] += i['below25k_old']
        baseline[t]['college_diff'] += i['college_old']
        baseline[t]['foreignborn_diff'] += i['foreignborn_old']
        baseline[t]['renteroccupied_diff'] += i['renteroccupied_old']      
        baseline[t]['last10yrs_diff'] += i['last10yrs_old']  
        baseline[t]['vacancy_diff'] += i['vacancy_old']  
        baseline[t]['professional_diff'] += i['professional_old'] 
        baseline[t]['new_residents_diff'] += i['new_residents_old']
        baseline[t]['non_english_diff'] += i['non_english_old']
        if i['median_income_old'] > -100000 and i['median_income_old'] < 100000:
          baseline[t]['median_income_diff'] += i['median_income_old']
        else:
          baseline[t]['median_income_diff'] += baseline[t]['median_income_diff']/baseline[t]['count']
        if i['travel_time_old'] > 0 and i['travel_time_old'] < 1000:
          baseline[t]['travel_time_diff'] += i['travel_time_old']
        else:
          baseline[t]['travel_time_diff'] += baseline[t]['travel_time_diff']/baseline[t]['count']
        if i['avg_rent_old'] > 0 and i['avg_rent_old'] < 10000:
          baseline[t]['avg_rent_diff'] += i['avg_rent_old']
        else:
          baseline[t]['avg_rent_diff'] += baseline[t]['avg_rent_diff']/baseline[t]['count']
    for t in typologies:
        print(t)
        for key in totals[t]:
            if key=='count':
              print(key,totals[t][key])
            else:
              print(key,(totals[t][key]/totals[t]['count'])/(baseline[t][key]/baseline[t]['count']))



if __name__ == '__main__':
  #for metro_area in os.listdir('./html'):
     # print(metro_area)
     # metro_area_data(metro_area)


  testing('chicago')
  #metro_area_data('chicago')