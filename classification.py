import csv
import os
import numpy as np
from collections import defaultdict
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfTransformer,CountVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold
#from imblearn import under_sampling
from imblearn.under_sampling import RandomUnderSampler

def classify_typology(typology):
    if typology in ['Low-Income/Susceptible to Displacement', 'Ongoing Displacement','At Risk of Gentrification']:
        t = 'Low'
    elif typology in ['Early/Ongoing Gentrification', 'Advanced Gentrification','Stable Moderate/Mixed Income','High Student Population']:
        t = 'Mixed'
    elif typology in ['At Risk of Becoming Exclusive','Becoming Exclusive','Stable/Advanced Exclusive']:
        t = 'Exclusive'
    else:
        t = 'Other'
    return t

def process_body(body):
    body =body[2:-2]
    body = body.split('\', \'')
    body = ' '.join(body)
    return body

def gather_data(mode): #settings: 3types, 9types, poverty, race
  X = []
  y = []
  options = defaultdict(int)
  for filename in os.listdir('./csv'):
    #if filename == 'chicago_complete.csv':
      with open('./csv/'+filename,'r') as csvfile:
          reader = csv.DictReader(csvfile)
          for row in reader:
            if mode == '3types' or mode == '9types':
                t = row.get('typology','NA')
            else:
                t = row.get(mode,'NA')
                
            t=t.strip()
            

            if t not in ['NA','','Other', 'None', 'Unavailable or Unreliable Data']:
              if mode == '3types': 
                t = classify_typology(t)
                
              options[t] +=1  
              
              body = process_body(row['posting_body'])
              X.append(body)
              y.append(t)
  print(mode,len(X),options)
  return np.array(X,dtype=str),np.array(y,dtype = str)

def train(mode):
    X,y = gather_data(mode)
    
    X_new = X.reshape(-1,1)
    rus = RandomUnderSampler(random_state=0)
    X_resampled, y_resampled = rus.fit_resample(X_new, y)
    
    text_clf = Pipeline([
        ('vect', CountVectorizer()),
        ('tfidf',TfidfTransformer()),
        ('clf', SGDClassifier(loss='hinge',penalty='l2',alpha=1e-3,random_state=42,max_iter = 5,tol=None))
        ])

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = []
    for train_index, test_index in skf.split(X_resampled, y_resampled):
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]
        text_clf.fit(X_train, y_train)
        scores.append(text_clf.score(X_test, y_test))
    print(mode, np.mean(scores))
   # return np.mean(scores),clf,X_resampled, y_resampled


if __name__ == '__main__':
  for mode in ['poverty','race','3types','9types']:
    train(mode)
    #gather_data(mode)
    
    