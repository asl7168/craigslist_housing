from text_processing import process_html,jsons_to_csv 
from demographics_multistate import get_demographics 
from state_codes import state_codes
import json
import os
import csv
from collections import defaultdict

#state codes: https://www.nlsinfo.org/content/cohorts/nlsy97/other-documentation/geocode-codebook-supplement/attachment-100-census-bureau

def metro_area_data(metro_area):
  process_html("./html/"+metro_area)
  print("1")
  jsons_to_csv("./json/"+metro_area)
  print("2")
  states = state_codes[metro_area]
  data = get_demographics(metro_area,states)
  #print(data['3790493246'])
  
  #if not os.path.exists(f"./json_complete/{metro_area}"): os.makedirs(f"./json_complete/{metro_area}")
  
  #for key in data:
      #json_obj = json.dumps(data[key], indent=1)
      #json_path = f"./json_complete/{metro_area}/{key}.json"

      #with open(json_path, "w") as outfile:
      #    outfile.write(json_obj)
  with open(f'./csv_dumps/all_complete.csv','a') as csvfile:
      fieldnames = ['documents','poverty','race','class','is_white','college','foreignborn','renteroccupied','last10yrs','vacancy','rent']
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
            'last10yrs': item['last10yrs'],
            'vacancy': item['vacancy'],
            'rent': 'NA' if item['price']=='NA' else float(item['price'])/1000
          }
          if item['poverty'] != 'NA' and obj['rent'] != 'NA' and obj['rent']<=10:
            writer.writerow(obj)

def testing(metro_area):
    states = state_codes[metro_area]
    data = get_demographics(metro_area,states)
    typologies = ['Advanced Gentrification','At Risk of Becoming Exclusive','At Risk of Gentrification','Becoming Exclusive','Early/Ongoing Gentrification','High Student Population','Low-Income/Susceptible to Displacement','Ongoing Displacement','Stable Moderate/Mixed Income','Advanced Exclusive','Unavailable or Unreliable Data','Stable/Advanced Exclusive','None']
    new = {}
    old={}
    for t in typologies:
      new[t] = defaultdict(float)
      old[t] = defaultdict(float)
    print("here")
    for key in data:
      i = data[key]
      if i['white']!='NA' and i['white_diff']!='NA':
        t = i['typology']
        new[t]['count'] += 1
        new[t]['white'] += i['white']
        new[t]['black'] += i['black']
        new[t]['asian'] += i['asian']
        new[t]['latinx'] += i['latinx']
        new[t]['below25k'] += i['below25k']
        new[t]['college_diff'] += i['college_diff']
        new[t]['foreignborn_diff'] += i['foreignborn_diff']
        new[t]['renteroccupied_diff'] += i['renteroccupied_diff']      
        new[t]['last10yrs_diff'] += i['last10yrs_diff'] 
        new[t]['vacancy_diff'] += i['vacancy_diff']  
        new[t]['professional_diff'] += i['professional_diff'] 
        new[t]['new_residents_diff'] += i['new_residents_diff']
        new[t]['non_english_diff'] += i['non_english_diff']

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
        for key in totals[t]:
            if key=='count':
              print(key,new[t][key])
            else:
              print(key,(new[t][key]-old[t][key])/(old[t][key]))



if __name__ == '__main__':
  for metro_area in os.listdir('./html'):
      print(metro_area)
      metro_area_data(metro_area)


  #testing('chicago')
  #metro_area_data('chicago')