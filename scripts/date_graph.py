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
import numpy as np

def date_graph():
  df=pd.DataFrame({'date':[]})
  for metro_area in os.listdir(f'{html_prefix}/html'):
    
    #path = f"{prefix}/csv_dumps/{metro_area}_csv_dump.csv"
    #new_df = pd.read_csv(path,dtype = str)
    #new_df[['date','time']] = new_df['posted'].str.split(" ",expand=True)
    
    #df = pd.concat([df,new_df[['date']]])
    path = f"{prefix}/csv/{metro_area}_complete.csv"
    new_df = pd.read_csv(path,dtype = str)
    new_df[['date','time']] = new_df['posted'].str.split(" ",expand=True)
    print(metro_area,len(new_df))
    df = pd.concat([df,new_df[['date']]])
  
  
  
  print(df.shape)
  print(df.head())
  print(df.columns)
  df['date']=pd.to_datetime(df['date'])
  print(df['date'].min(),df['date'].max())
  #df['tmp'] = df[df.date.notnull()]
  #print(df.shape)
  #df.set_index(['date'], inplace=True)
  #print(df.head())
  # for '1M' for 1 month; '1W' for 1 week; check documentation on offset alias
  df['date'].hist(bins=30)
  #df.hist('date',bins=30)
  plt.savefig('/projects/p31502/projects/craigslist/scripts/dates_complete.png')
    
def write_metro_areas():
  areas = []
  for metro_area in os.listdir(f'{html_prefix}/html'):
    areas.append(metro_area)
  with open("/projects/p31502/projects/craigslist/scripts/metro_areas.txt",'w') as outfile:
    for a in areas:
      outfile.write(a+"\n")

def find_missing():
  total_found=0
  total_missing=0
  total_repost=0
  #for metro_area in os.listdir(f'{html_prefix}/html'):
  metro_area='buffalo'
    #print(metro_area) 
  #if metro_area!='seattle':
  path = f"{prefix}/csv/{metro_area}_complete.csv"
  df = pd.read_csv(path,dtype = str)
  html=[]
  for filename in os.listdir(f'{html_prefix}/read_html/{metro_area}'):
    html.append(filename.split("_")[-1])
  reposts=[]
  for filename in os.listdir(f'{html_prefix}/repost_html/{metro_area}'):
    reposts.append(filename.split("_")[-1])
  ids = df['post_id'].values.tolist()
  print(len(ids))
  found=0
  missing=0
  repost=0
  missing_list=[]
  for post_id in ids:
    if post_id in html:
      found+=1
    elif post_id in reposts:
      repost+=1
    else:
      missing+=1
      missing_list.append(post_id)
  print(metro_area,found,repost,missing,missing_list[-5:])
  total_found+=found
  total_repost+=repost
  total_missing+=missing
  print(total_found,total_repost,total_missing)
    

def count_html():
  html_count=0
  read_html_count=0
  repost_html_count=0
  problem_html_count=0
  post_count=0

  for metro_area in os.listdir(f'{html_prefix}/html'):
  #metro_area='seattle'
    
    
    for filename in os.listdir(f'{html_prefix}/html/{metro_area}'):
      html_count+=1
      print(metro_area,filename)
    for filename in os.listdir(f'{html_prefix}/read_html/{metro_area}'):
      read_html_count+=1
    for filename in os.listdir(f'{html_prefix}/repost_html/{metro_area}'):
      repost_html_count+=1
    for filename in os.listdir(f'{html_prefix}/problem_html/{metro_area}'):
      problem_html_count+=1
    path = f"{prefix}/csv/{metro_area}_complete.csv"
    new_df = pd.read_csv(path,dtype = str)
    post_count+=len(new_df)
    
  print(html_count,read_html_count,repost_html_count,problem_html_count,post_count)

def drop_duplicates():
  print("starting")
  for metro_area in os.listdir(f'{html_prefix}/html'):
    path = f"{prefix}/csv/{metro_area}_complete.csv"
    df = pd.read_csv(path)
    df['has_duplicates']=df.duplicated(subset=['title','price','map_address','street_address','latitude','longitude','available','housing_type','bedrooms','bathrooms','laundry','parking','sqft','flooring','rent_period','posting_body'],keep=False)
    new_df = df.drop_duplicates(subset=['title','price','map_address','street_address','latitude','longitude','available','housing_type','bedrooms','bathrooms','laundry','parking','sqft','flooring','rent_period','posting_body'])
    new_df.to_csv(f"{prefix}/csv_no_duplicates/{metro_area}_complete.csv")
    print(metro_area,len(df),len(new_df))

def get_counts():
  duplicates=[]
  for metro_area in os.listdir(f'{html_prefix}/html'):
    print(metro_area)
    df1=pd.read_csv(f"{prefix}/csv/{metro_area}_complete.csv")
    df2=pd.read_csv(f"{prefix}/csv_no_duplicates/{metro_area}_complete.csv")
    duplicates.append(len(df1)-len(df2))
  duplicates = np.array(duplicates)
  print(np.sum(duplicates),np.mean(duplicates))
#date_graph()
#write_metro_areas()
#count_html()
#find_missing()
#drop_duplicates()
get_counts()