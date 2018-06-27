# -*- coding: utf-8 -*-
"""
Created on Wed May 16 09:20:07 2018

@author: Guillaume
"""

from learn_tree_funcs import get_data_size, get_feature_value, get_target, get_leaf_parents, get_path
from collections import Counter
import time
import numpy as np
    
                                            
class pattern:
    
    def __init__(self,ending_leaf,F_vector,correct,rows,target):
        
        self.leaf = ending_leaf #integer
        self.F = F_vector #list of tuples (feature,feature_value_indicator) = (integer,integer)
        self.c = correct #integer
        self.R = rows #list of rows (integer)
        self.target = target #integer
        self.e = len(self.R) - self.c #error, integer
        
    def __str__(self):
        
        return "Ending leaf: " + str(self.leaf) +"\nF_vector: " + str(self.F) + "\nPredicted target index: " + str(self.target) + "\nCorrect predictions: " +str(self.c) + "\nRows: " +str(self.R)
    
    def add_missing_rows(self,depth,C_set): #compute the exact pattern given the one provided by the pricing
    
        data_size = get_data_size()
                        
        bin_l = bin(self.leaf)[2:].zfill(depth)
        
        parents = get_leaf_parents(self.leaf,len(C_set))
        
        for r in range(data_size):
            
            #if r not in self.R: #check if this row has to be included
                
            incl = True
            
            for h in range(depth):
                
                j = parents[-1-h]
                
                (i,v) = self.F[h]
                                                                        
                if get_feature_value(r,i) <= C_set[j][i][v] and bin_l[h]=='1':
                    
                    incl = False
                    
                    break
                    
                elif get_feature_value(r,i) > C_set[j][i][v] and bin_l[h]=='0':
                    
                    incl = False
                    
                    break
                
            if incl:
                
                self.R.append(r)
                    
    def add_missing_rows2(self,depth,C_set,DATA): #compute the exact pattern given the one provided by the pricing
            
        data_size = len(DATA)
        
        bin_l = bin(self.leaf)[2:].zfill(depth)
        
        parents = get_leaf_parents(self.leaf,len(C_set))
        
        for r in range(data_size):
            
            #if r not in self.R: #check if this row has to be included
                
            incl = True
            
            for h in range(depth):
                
                j = parents[-1-h]
                
                (i,v) = self.F[h]
                                                        
                if get_feature_value(r,i) <= C_set[j][i][v] and bin_l[h]=='1':
                    
                    incl = False
                    
                    break
                    
                elif get_feature_value(r,i) > C_set[j][i][v] and bin_l[h]=='0':
                    
                    incl = False
                    
                    break
                
            if incl:
                
                self.R.append(r)
                    
    def score(self):
        
        return(sum([get_target(r)==self.target for r in self.R]))
                    
                    
    def pred_target(self):
                    
        targets = [get_target(r) for r in self.R]
            
        try:
            
            pred = Counter(targets).most_common(1)[0][0]
            
        except(IndexError): #empty list
            
            pred = 0
                
        c = sum([1 for r in self.R if get_target(r)==pred])
        
        self.c = c
        self.target = pred
        self.e = len(self.R) - self.c