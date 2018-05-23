# -*- coding: utf-8 -*-
"""
Created on Wed May 16 09:20:07 2018

@author: Guillaume
"""

from learn_tree_funcs import get_data_size, get_feature_value

class pattern:
    
    def __init__(self,ending_leaf,F_vector,correct,rows,target):
        
        self.leaf = ending_leaf #integer
        self.F = F_vector #list of tuples (feature,feature_value_indicator) = (integer,integer)
        self.c = correct #integer
        self.R = rows #list of rows (integer)
        self.target = target #integer
        
    def __str__(self):
        
        return "Ending leaf: " + str(self.leaf) +"\nF_vector: " + str(self.F) + "\nPredicted target index: " + str(self.target) + "\nCorrect predictions: " +str(self.c) + "\nRows: " +str(self.R)
    
    def add_missing_rows(self,depth,C_set): #compute the exact pattern given the one provided by the pricing
    
        data_size = get_data_size()
                
        bin_l = bin(self.leaf)[2:].zfill(depth)
        
        for r in range(data_size):
            
            if r not in self.R: #check if this row has to be included
                
                incl = True
                
                for h in range(depth):
                    
                    (i,v) = self.F[h]
                    
                    if get_feature_value(r,i) <= C_set[i][v] and bin_l[h]=='1':
                        
                        incl = False
                        
                    if get_feature_value(r,i) > C_set[i][v] and bin_l[h]=='0':
                        
                        incl = False
                        
                if incl:
                    
                    self.R.append(r)