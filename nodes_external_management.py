# -*- coding: utf-8 -*-
"""
Created on Tue Apr 17 11:27:19 2018

@author: Guillaume
"""

from learn_tree_funcs import get_data_size, get_num_features, get_leaf_parents, get_target
import random
from pattern import pattern
from collections import Counter

"""HASH FUNCTIONS"""


def init_rand_hash(depth,num_features,C_set):
    random.seed(0)
    global rand_hash
    rand_hash = [[[random.random() for v in range(len(C_set[i]))] for i in range(num_features)] for h in range(depth)]

def hash_pattern(pattern):
        
    return sum([rand_hash[h][pattern.F[h][0]][pattern.F[h][1]] for h in range(len(pattern.F))]) + 3*pattern.leaf +2.2568*pattern.target



"""TOOL FUNCTIONS"""


def color_leaf(l):
    
    if l==0:
        
        return 'b'
    
    elif l==1:
    
        return 'r'
    
    elif l==2:
    
        return 'y'
    
    else:
        
        return 'm'
      

"""EXTRACTING PATTERNS FROM THE SOLUTION AND THE SOLUTION TYPE"""   


def extract_pattern_pricing(pricing_prob,leaf,depth,C_set):
    
    num_features = get_num_features()
    
    data_size = get_data_size()
    
    R, F = [], []
    
    for r in range(data_size):
    
        if "row_"+str(r) in pricing_prob.variables.get_names() and 0.99 <= float(pricing_prob.solution.get_values("row_"+str(r))) <= 1.01:
        
            R.append(r)
                
    for h in range(depth):
    
        for i in range(num_features):
        
            for v in range(len(C_set[i])):
                
                if 0.99 <= float(pricing_prob.solution.get_values("u_"+str(i)+"_"+str(h)+"_"+str(v))) <= 1.01:
                    
                    F.append((i,v))
                    
    targets = [get_target(r) for r in R]
        
    pred = Counter(targets).most_common(1)[0][0]
            
    c = sum([1 for r in R if get_target(r)==pred])
                    
    p = pattern(leaf,F,c,R,pred)
            
    return p
            
            
    

def give_solution_type(prob): #return a string saying if the solution is integral, continuous or infeasible
    
    if "infeasible" in prob.solution.status[prob.solution.get_status()]:

        return "infeasible"
    
    else:
        
        for v in prob.variables.get_names():
            
            i = prob.solution.get_values(v)
            
            if ((float(i) <= round(i) - 0.01) or (float(i) >= round(i) + 0.01)):
                
                return "continuous"
            
        return "integer"
    