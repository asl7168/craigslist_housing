import os, sys
QUEST_path = "/projects/p31502/projects/craigslist"
if os.path.exists(QUEST_path): 
    sys.path.append(QUEST_path)
    prefix = QUEST_path
    html_prefix = "/projects/b1170/corpora/craigslist"
else:
    prefix = "."
    html_prefix = prefix
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm

def filter_html(metro_area=None):
  if not metro_area:
    for metro_area in os.listdir(f'{html_prefix}/html'):
      print(metro_area)
      filtering(metro_area)
  else:
    filtering(metro_area)
    
  

def filtering(metro_area):
  print(metro_area)

  path1 = f"{prefix}/csv/{metro_area}_complete.csv"
  new_df = pd.read_csv(path1,dtype = str)
  processed_ids = list(new_df['post_id']) #+processed_ids
  
  print(len(processed_ids))
  
  if not os.path.exists(f"{html_prefix}/read_html/"+metro_area):
    os.makedirs(f"{html_prefix}/read_html/"+metro_area)
  count_all=0
  count_renamed=0
  index = 0
  for filename in tqdm(os.listdir(f"{html_prefix}/html/"+metro_area), desc=f"Processing html from {metro_area}..."):
    filepath = os.path.join(f"{html_prefix}/html/"+metro_area, filename)
    if not os.path.isfile(filepath): continue
    count_all+=1
    #if len(filename.split("_"))>1:
     # index +=1
      #if index<5:
       # print(filename,filename.split("_")[-1] in processed_ids)
    if filename.split("_")[-1] in processed_ids:
      os.rename(filepath,os.path.join(f"{html_prefix}/read_html/"+metro_area,filename))
      count_renamed+=1
    #else:
    #  print(filename)
  print(count_all,count_renamed)
  
def reverse_filter(metro_area):
  print(metro_area)
  #path = f"{prefix}/csv_dumps/{metro_area}_csv_dump.csv"
  #df = pd.read_csv(path,dtype = str)
  #processed_ids = list(df["post_id"])

  path1 = f"{prefix}/csv/{metro_area}_complete.csv"
  new_df = pd.read_csv(path1,dtype = str)
  processed_ids = list(new_df['post_id']) #+processed_ids
  
  print(len(processed_ids))
  
  count_all=0
  count_renamed=0
  index = 0
  for filename in tqdm(os.listdir(f"{html_prefix}/read_html/"+metro_area), desc=f"Processing html from {metro_area}..."):
    filepath = os.path.join(f"{html_prefix}/read_html/"+metro_area, filename)
    if not os.path.isfile(filepath): continue
    count_all+=1
    #if len(filename.split("_"))>1:
     # index +=1
      #if index<5:
       # print(filename,filename.split("_")[-1] in processed_ids)
    if filename.split("_")[-1] not in processed_ids:
      os.rename(filepath,os.path.join(f"{html_prefix}/html/"+metro_area,filename))
      count_renamed+=1
  print(count_all,count_renamed)

#filter_html('inlandempire')

def move_html(metro_area):
  for filename in tqdm(os.listdir(f"{html_prefix}/read_html/"+metro_area), desc=f"Processing html from {metro_area}..."):
    filepath = os.path.join(f"{html_prefix}/read_html/"+metro_area, filename)
    if not os.path.isfile(filepath): continue
    #count_all+=1
    #if len(filename.split("_"))>1:
     # index +=1
      #if index<5:
       # print(filename,filename.split("_")[-1] in processed_ids)
    os.rename(filepath,os.path.join(f"{html_prefix}/html/"+metro_area,filename))
    #count_renamed+=1
    
#move_html('seattle')
#move_html('sfbay')
#filter_html('cincinnati')
  