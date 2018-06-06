# -*- coding: utf-8 -*-
"""
Created on Tue Apr 17 11:27:19 2018

@author: Guillaume
"""

from learn_tree_funcs import get_data_size, get_num_features, get_leaf_parents, get_target
import random
from pattern import pattern
import numpy as np
import time

"""HASH FUNCTIONS"""


def init_rand_hash(depth,num_features,C_set):
    random.seed(0)
    global rand_hash
    rand_hash = [[[random.random() for v in range(len(C_set[i]))] for i in range(num_features)] for h in range(depth)]

def hash_pattern(pattern):
        
    return sum([rand_hash[h][pattern.F[h][0]][pattern.F[h][1]] for h in range(len(pattern.F))]) + 3*pattern.leaf +2.2568*pattern.target + 15.256*len(pattern.R)



"""TOOL FUNCTIONS"""

from matplotlib import colors as mcolors


colors = dict(mcolors.BASE_COLORS, **mcolors.CSS4_COLORS)
by_hsv = sorted((tuple(mcolors.rgb_to_hsv(mcolors.to_rgba(color)[:3])), name)
                for name, color in colors.items())
sorted_names = [name for hsv, name in by_hsv]


def color_leaf(l,t,depth):
    
    num_leafs = 2**depth
    
    return colors[sorted_names[4*l + 4*num_leafs*t]]
      

"""EXTRACTING PATTERNS FROM THE SOLUTION AND THE SOLUTION TYPE"""   


def extract_pattern_pricing(pricing_prob,leaf,depth,C_set):
            
    num_features = get_num_features()
    
    R, F = [], [0 for h in range(depth)]
    
    """
    
    Rbis, Fbis = [], []
    
    for r in range(get_data_size()):
    
        if "row_"+str(r) in pricing_prob.variables.get_names() and 0.99 <= float(pricing_prob.solution.get_values("row_"+str(r))) <= 1.01:
        
            Rbis.append(r)
                
    for h in range(depth):
    
        for i in range(num_features):
        
            for v in range(len(C_set[i])):
                
                if 0.99 <= float(pricing_prob.solution.get_values("u_"+str(i)+"_"+str(h)+"_"+str(v))) <= 1.01:
                    
                    Fbis.append((i,v))
                    
    """
                
    sol=pricing_prob.solution.get_values(depth*sum([len(C_set[i]) for i in range(num_features)]),pricing_prob.variables.get_num()-1)
        
    sol=np.array(sol)
    
    index = np.where(sol > 0.99)[0]
    
    for idx in index:
    
        var_name = pricing_prob.variables.get_names(depth*sum([len(C_set[i]) for i in range(num_features)])+int(idx))
                
        tmp=var_name.split("_")
        
        row = int(tmp[-1])
        
        R.append(row)

    sol=pricing_prob.solution.get_values(0,depth*sum([len(C_set[f]) for f in range(num_features)])-1)
                
    sol=np.array(sol)
        
    index = np.where(sol > 0.99)[0]
        
    for idx in index:
                
        var_name = pricing_prob.variables.get_names(int(idx))
        
        tmp=var_name.split("_")
        
        (i,v) = (int(tmp[-3]),int(tmp[-1]))
        
        F[int(tmp[-2])] = (i,v)
        
    #print(F,Fbis)
        
    #assert R==Rbis
    
    #assert F==Fbis
                        
    p = pattern(leaf,F,0,R,0) #target and score will be computed in the next function
            
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
    