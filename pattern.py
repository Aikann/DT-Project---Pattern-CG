# -*- coding: utf-8 -*- 
"""
Created on Wed May 16 09:20:07 2018

@author: Guillaume
"""

from learn_tree_funcs import get_data_size, get_feature_value, get_target, get_leaf_parents
from collections import Counter
    
                                            
class pattern:
    
    def __init__(self,ending_leaf,F_vector,correct,rows,target):
        """ Construct a path
    
        Input:
            ending_leaf (integer): ending leaf of the pattern
            F_vector (list of tuples): decision splits along the path
            correct (integer): number of correct predictions
            rows (list of integers): rows passing through the path
            target (integer): index of the prediction
            
        Output:
            self (pattern)
        """
        
        self.leaf = ending_leaf #integer
        self.F = F_vector #list of tuples (feature,feature_value_indicator) = (integer,integer)
        self.c = correct #integer
        self.R = rows #list of rows (integer)
        self.target = target #integer
        self.e = len(self.R) - self.c #error, integer
        
    def __str__(self):
        """Print method
        
        Input:
            none
            
        Output:
            none
        """
        
        return "Ending leaf: " + str(self.leaf) +"\nF_vector: " + str(self.F) + "\nPredicted target index: " + str(self.target) + "\nCorrect predictions: " +str(self.c) + "\nRows: " +str(self.R)
    
    def add_missing_rows(self,depth,C_set):
        """ Compute rows for a path knowing only the decision splits
    
        Input:
            depth (integer): maximum depth of the tree
            C_set (list of list of list of floats): restricted thresholds set
            
        Output:
            none (works in place)
        """
    
        data_size = get_data_size()
                        
        bin_l = bin(self.leaf)[2:].zfill(depth)
        
        parents = get_leaf_parents(self.leaf,len(C_set))
        
        for r in range(data_size):
                            
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
        """ Compute score for a given path
    
        Input:
            none
            
        Output:
            correct (integer): number of correctly predicted rows
        """
        
        return(sum([get_target(r)==self.target for r in self.R]))
                    
                    
    def pred_target(self):
        """ Compute target for a given path
    
        Input:
            none
            
        Output:
            none (works in place)
        """
                    
        targets = [get_target(r) for r in self.R]
            
        try:
            
            pred = Counter(targets).most_common(1)[0][0]
            
        except(IndexError): #empty list
            
            pred = 0
                
        c = sum([1 for r in self.R if get_target(r)==pred])
        
        self.c = c
        self.target = pred
        self.e = len(self.R) - self.c