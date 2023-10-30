import os, sys
QUEST_path = "/projects/p31502/projects/craigslist"
if os.path.exists(QUEST_path): 
    sys.path.append(QUEST_path)
    prefix = QUEST_path
    html_prefix = "/projects/b1170/corpora/craigslist"
else:
    prefix = "."
    html_prefix = prefix

#import spacy
#nlp = spacy.load('en_core_web_lg')


import csv
import pandas as pd
from scipy import stats
import numpy as np
import re

import requests
from GIS_data.state_codes import state_codes
import tiktoken

encoding = tiktoken.get_encoding("r50k_base")  # remove prompts > 2048 tokens



def get_data(state,county,tract):
  r_new = requests.get('https://api.census.gov/data/2021/acs/acs5/profile?get=DP03_0062E,DP05_0064PE,DP05_0065PE,DP05_0067PE,DP05_0071PE&for=tract:'+tract+'&in=state:'+state+'%20county:'+county+'&key=901e1c41a36cd6bbee390e6cc013021757d66ffd')
  #r_new = requests.get('https://api.census.gov/data/2021/acs/acs5/profile?get=DP03_0062E,DP05_0037PE&for=tract:'+tract+'&in=state:'+state+'%20county:'+county+'&key=901e1c41a36cd6bbee390e6cc013021757d66ffd')
  
  try:
      data = r_new.json()
  except requests.exceptions.JSONDecodeError:
      return {}
  classifications={}
  for i,items in enumerate(data[1:]):
    name = items[5]+items[6]+items[7]
    #name = items[2]+items[3]+items[4]
    if any([float(i)<0 for i in items]):
      continue
    race_vals = {
      'white': float(items[1]),
      'POC': float(items[2])+float(items[3])+float(items[4])
    }
    income= float(items[0])
    race=max(race_vals,key = race_vals.get)
    #race = 'white' if float(items[1])>60 else 'POC'
    classifications[name]={
      'income':income,
      'race':race
    }
    if i<10:
      print(income,race)
  return classifications

def income_classes(row):
  if row['income']<-.5:
    return 'low'
  elif row['income']>.5:
    return 'high'
  else:
    return 'average'
    
def score(x):
  #print(x.mean(),x.min(),x.max())
  #print(x.shape)
  score_set = np.array(list(set(x)))
  return (x - score_set.mean()) / score_set.std()

def update_demographics(metro_area):
  states = state_codes[metro_area]
  demographics=get_data(states[0],'*','*')
  path = f"{prefix}/csv_no_duplicates/{metro_area}_complete.csv"
  df = pd.read_csv(path)
  df = df[['post_id','title','price','bedrooms','posting_body','GEOID']]
  beds=df['bedrooms'].value_counts().first_valid_index()
  print(df['bedrooms'].value_counts())
  df=df.loc[df['bedrooms']==beds]
  df=df.dropna(subset=['GEOID','price'])
  df['GEOID']=df['GEOID'].astype(int)
  count_df=df.groupby(['GEOID']).count()
  count_df=count_df.loc[count_df['post_id']>9]
  geoids=count_df.index.tolist()
  df = df.loc[df['GEOID'].isin(geoids)]
  zscore = lambda x: (x - x.mean()) / x.std()
  df.insert(4,'rent',df.groupby(['GEOID'])['price'].transform(zscore))
  df.insert(4,'avg_rent',df.groupby(['GEOID'])['price'].transform('mean'))
  df=df.dropna(subset=['rent'])
  df.to_csv(f'/projects/p31502/projects/craigslist/LLM_data/{metro_area}.csv',index=False)
  data =[]
  missing=0
  m=[]
  with open(f'/projects/p31502/projects/craigslist/LLM_data/{metro_area}.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      geoid = str(row['GEOID'])
      demo = demographics.get(geoid,None)
      if demo:
        obj=row
        rent = float(obj['rent'])
        obj['rent_class']='expensive' if rent>.5 else 'cheap' if rent<-.5 else 'average'
        obj['income_raw']=demo['income']
        obj['race']=demo['race']
        data.append(obj)
      else:
        missing+=1
        m.append(geoid)
  print(missing,len(list(set(m))))
  df = pd.DataFrame(data)
  df['income']=score(df['income_raw'])#stats.zscore(df['income_raw'])
  print(df['income_raw'].mean())
  df['income_class']=df.apply(lambda x:income_classes(x),axis=1)
  df.to_csv(f'/projects/p31502/projects/craigslist/LLM_data/{metro_area}_complete.csv',index=False)
  print(df['rent_class'].value_counts())
  print(df['income_class'].value_counts())
  print(df['race'].value_counts())
  df=df[['post_id','title','posting_body','rent_class','income_class','race']]
  df.to_csv(f'/projects/p31502/projects/craigslist/LLM_data/{metro_area}_prepared.csv',index=False)
        
def get_stats(metro_area):
  df1 =pd.read_csv(f'/projects/p31502/projects/craigslist/LLM_data/{metro_area}_prepared.csv')  
  print(df1['rent_class'].value_counts())
  print(df1['income_class'].value_counts())
  print(df1['race'].value_counts())
  df2 =pd.read_csv(f'/projects/p31502/projects/craigslist/LLM_data/{metro_area}_prepared_old.csv') 
  print(df2['rent_class'].value_counts())
  print(df2['income_class'].value_counts())
  print(df2['race'].value_counts())
  print(df1.shape,df2.shape)

def drop_duplicates(metro_area):
  df=pd.read_csv(f'/projects/p31502/projects/craigslist/LLM_data/{metro_area}_prepared.csv') 
  print(df.shape)
  #print(df['posting_body'].value_counts().head())
  new_df = df.drop_duplicates(subset=['posting_body','rent_class','income_class','race'])
  #new_df = df.drop_duplicates(subset=['posting_body','title'])
  new_df.to_csv(f'/projects/p31502/projects/craigslist/LLM_data/{metro_area}_clean.csv',index=False)
  print(new_df.shape)
  #print(df.drop_duplicates(subset=['posting_body','title']).shape)

def clean_text(metro_area):
  places = get_lists(metro_area)
  data=[]
  with open(f'/projects/p31502/projects/craigslist/LLM_data/{metro_area}_clean.csv','r') as csvfile:
    reader = csv.DictReader(csvfile)
    for i,row in enumerate(reader):
        if i%100==0:
          print(i)
        obj = row
        for key in ['title','posting_body']:
          text = row[key]
          text = re.sub(r'^\[\'','',text)
          text = re.sub(r'\'\]$','',text)
          text = re.sub(r'\', \'',' ' ,text)
          #text = re.sub(r'\$\s?(\d,?(\.\d+)?){1,}',"PRICE",text)
          obj[key]=transform_texts(text,places)
          
        #obj['race']='Non-White' if row['race']=='POC' else 'White'
        data.append(obj)
        if i<10:
          print(obj)
  with open(f'/projects/p31502/projects/craigslist/LLM_data/{metro_area}_clean.csv','w') as csvfile:
    writer = csv.DictWriter(csvfile,fieldnames=['post_id','title','posting_body','rent_class','income_class','race'])
    writer.writeheader()
    for d in data:
      writer.writerow(d)
  df = pd.read_csv(f'/projects/p31502/projects/craigslist/LLM_data/{metro_area}_clean.csv')
  print(df.shape)
  
  def tokenize_body(body):
    return len(encoding.encode(body))
  print(df.columns)
  df["body_tokens"] = df["posting_body"].apply(tokenize_body)
  df = df.astype({"title": "string", "posting_body": "string", "rent_class": "string", 
                  "income_class": "string", "race": "string", "body_tokens": "int"})
  df = df[df["body_tokens"] <= 2048]
  df = df[['post_id','title','posting_body','rent_class','income_class','race']]
  
  #print(df['posting_body'].value_counts())
  new_df = df.drop_duplicates(subset=['posting_body','rent_class','income_class','race'])
  new_df.to_csv(f'/projects/p31502/projects/craigslist/LLM_data/{metro_area}_clean.csv',index=False)
  print(new_df.shape)

def adjust_titles(metro_area):
  places = get_lists(metro_area)
  data={}
  with open(f'/projects/p31502/projects/craigslist/LLM_data/{metro_area}_clean.csv','r') as csvfile:
    reader = csv.DictReader(csvfile)
    for i,row in enumerate(reader):
        if i%100==0:
          print(i)
        obj = row
        for key in ['title']:
          text = row[key]
          text = re.sub(r'^\[\'','',text)
          text = re.sub(r'\'\]$','',text)
          text = re.sub(r'\', \'',' ' ,text)
          #text = re.sub(r'\$\s?(\d,?(\.\d+)?){1,}',"PRICE",text)
          obj[key]=transform_texts(text,places)
        obj['race']='Non-White' if row['race']=='POC' else 'White'
        data[obj['post_id']]=obj
  errors=0
  with open(f'/projects/p31502/projects/craigslist/LLM_data/{metro_area}_masked.csv','r') as csvfile:
    reader = csv.DictReader(csvfile)
    for i,row in enumerate(reader):
      obj = data.get(row['post_id'],None)
      if obj:
        obj['posting_body']=row['posting_body']
        data[row['post_id']] = obj
      else:
        errors+=1
  data_list=[]
  for key in data:
    data_list.append(data[key])
  print(errors)
  df = pd.DataFrame(data_list)
  df.to_csv(f'/projects/p31502/projects/craigslist/LLM_data/{metro_area}_new.csv',index=False)
  print(df.head())
  
def remove_duplicates(metro_area):
  print("1")
  ids=[]
  with open(f'/projects/p31502/projects/craigslist/LLM_data/{metro_area}_masked_old.csv','r') as csvfile:
    reader = csv.DictReader(csvfile)
    for i,row in enumerate(reader):
      ids.append(row['post_id'])
  data = []
  print("2")
  with open(f'/projects/p31502/projects/craigslist/LLM_data/{metro_area}_new.csv','r') as csvfile:
    reader = csv.DictReader(csvfile)
    for i,row in enumerate(reader):
      if row['post_id'] in ids:
        data.append(row)
  df = pd.DataFrame(data)
  df.to_csv(f'/projects/p31502/projects/craigslist/LLM_data/{metro_area}_final.csv',index=False)
  print(df.shape)

def deduplication(metro_area):
  df = pd.read_csv(f'/projects/p31502/projects/craigslist/LLM_data/{metro_area}_final.csv')
  print(df.shape)
  df.to_csv(f'/projects/p31502/projects/craigslist/LLM_data/{metro_area}_final_old.csv',index=False)
  df = df.drop_duplicates(subset=['posting_body'])
  print(df.shape)
  df.to_csv(f'/projects/p31502/projects/craigslist/LLM_data/{metro_area}_final.csv',index=False)
  

def transform_texts(text,places):
  #ret = []
  #print('\t...transforming texts', end = ' ', flush=True)
  #for idx, text in enumerate(texts):
   #   if idx % 1000 == 0: print(idx, end = ' ', flush=True)
  #doc = nlp(text)
  #noent = ' '.join([t.text if not t.ent_type_ else t.ent_type_ for t in doc])
  noent = text
  noneigh = re.sub('[^A-Za-z]|[^A-Za-z]'.join(places), ' PLACE ', noent,flags = re.I)
  noneigh = re.sub('$|'.join(places)+"$", 'PLACE', noneigh,flags = re.I)
  noneigh = re.sub('^'+'|^'.join(places), 'PLACE', noneigh,flags = re.I)
  ret=re.sub('[0-9]+', 'num', noneigh)

  return ret 


def get_lists(metro_area):
  places=[]
  if metro_area=='chicago':
    places+=['pilsen','evanston',"skokie","arlington",'lakeview']
    with open("/projects/p31502/projects/craigslist/GIS_data/chicago_neighborhoods.csv",'r') as csvfile:
      reader = csv.DictReader(csvfile)
      for row in reader:
        places.append(row['PRI_NEIGH'])
        places+=row['SEC_NEIGH'].split(",")
  elif metro_area=='seattle':
    with open("/projects/p31502/projects/craigslist/GIS_data/seattle_neighborhoods.csv",'r') as csvfile:
      reader = csv.DictReader(csvfile)
      for row in reader:
        places.append(row['L_HOOD'])
        places.append(row['S_HOOD'])
        if row['S_HOOD_ALT_NAMES'] !='':
          places+=row['S_HOOD_ALT_NAMES'].split(", ")
  places=list(set(places))
  print(places)
  with open("/projects/p31502/projects/craigslist/GIS_data/us_cities.txt",'r') as infile:
    for row in infile:
      places.append(re.sub('\n','',row))
  places=list(set([p.strip().lower() for p in places]+[re.sub(' ','',p).lower() for p in places if len(p.split(" "))>1]))
  #print(places)
  return places 

    

#update_demographics("chicago") 
#get_stats('chicago')
#get_stats('seattle')
#drop_duplicates('chicago')
#adjust_titles('chicago')
#drop_duplicates('seattle')
#adjust_titles('seattle')
#clean_text('chicago')
#clean_text('seattle')
#get_lists('chicago')
#remove_duplicates('seattle')
deduplication('chicago')
deduplication('seattle')