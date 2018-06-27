# -*- coding: utf-8 -*-
"""
Created on Fri Jun 22 14:56:13 2018

@author: Guillaume
"""

from Instance import create_instance
import numpy as np
from sklearn.cross_validation import train_test_split
import pandas as pd

def test(tree,C_set,testfile):
    
    depth = int(np.log2(len(tree)))
    
    create_instance(testfile,test=True,inputdepth=depth)
            
    for p in tree:
        
        p.R = []
        
        p.add_missing_rows(depth,C_set)
        
        p.c = p.score()
        
    return float(sum([p.c for p in tree]))/sum([len(p.R) for p in tree])

def create_train_and_test(instance,nbr,DIR=''):
    
    trainfiles, testfiles = [], []
    
    df=pd.read_csv(instance,sep=';')
    
    for n in range(nbr):
    
        features = list(df.columns)
        target_feature = features[-1]
        features = list(features[:len(features)-1])
        
        y=df[target_feature]
        X=df[features]
        
        X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.25,train_size=0.5,random_state=10*n)
        
        train=pd.concat([X_train,y_train],axis=1)
                        
        train.to_csv(DIR+"train"+str(n)+".csv",sep=';',index=False,float_format='%.3f')
        
        trainfiles.append(DIR+"train"+str(n)+".csv")
        
        test=pd.concat([X_test,y_test],axis=1)
        
        test.to_csv(DIR+"test"+str(n)+".csv",sep=';',index=False,float_format='%.3f')
        
        testfiles.append(DIR+"test"+str(n)+".csv")
        
    return trainfiles, testfiles