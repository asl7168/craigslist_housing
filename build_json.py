from text_processing import process_html,jsons_to_csv 
from demographics_multistate import get_demographics 
from state_codes import state_codes
import json
import os

#state codes: https://www.nlsinfo.org/content/cohorts/nlsy97/other-documentation/geocode-codebook-supplement/attachment-100-census-bureau

def metro_area_data(metro_area):
  #process_html("./html/"+metro_area)
  #jsons_to_csv("./json/"+metro_area)
  states = state_codes[metro_area]
  data = get_demographics(metro_area,states)
  #print(data['3790493246'])
  
  if not os.path.exists(f"./json_complete/{metro_area}"): os.makedirs(f"./json_complete/{metro_area}")
  
  for key in data:
      json_obj = json.dumps(data[key], indent=1)
      json_path = f"./json_complete/{metro_area}/{key}.json"

      with open(json_path, "w") as outfile:
          outfile.write(json_obj)

if __name__ == '__main__':
  #for metro_area in os.listdir('./html'):
     # print(metro_area)
     # metro_area_data(metro_area)



  metro_area_data('chicago')