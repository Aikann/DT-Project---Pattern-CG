# -*- coding: utf-8 -*-
"""
Created on Tue Apr 17 11:27:19 2018

@author: Guillaume
"""

from learn_tree_funcs import get_data_size, get_num_features, get_leaf_parents
import random
from pattern import pattern
import numpy as np

"""HASH FUNCTIONS"""


def init_rand_hash(depth,num_features):
    """ Initialize the global hash table
    
    Input:
        depth (integer): maximum depth of the tree
        num_features (integer): number of features in the instance
        
    Output:
        none
    """
    
    random.seed(0)
    global rand_hash
    rand_hash = [[[random.random() for v in range(get_data_size())] for i in range(num_features)] for h in range(depth)]

def hash_pattern(pattern):
    """ Compute the hash value of a given path
    
    Input:
        pattern (pattern): path to hash
        
    Output:
        hash_value (float): hash value of the path
    """
        
    return sum([rand_hash[h][pattern.F[h][0]][pattern.F[h][1]] for h in range(len(pattern.F))]) + 3*pattern.leaf +2.2568*pattern.target + 15.256*len(pattern.R)

      

"""EXTRACTING PATTERNS FROM THE SOLUTION AND THE SOLUTION TYPE"""   


def extract_pattern_pricing(pricing_prob,leaf,depth,C_set):
    """ Extract the pattern object corresponding to a Cplex solution
    
    Input:
        pricing_prob (Cplex problem): already solved pricing problem
        leaf (integer): leaf of the path
        depth (integer): maximum depth of the tree
        C_set (list of list of list of floats): restricted thresholds set
        
    Output:
        p (pattern): corresponding path
    """
            
    num_features = get_num_features()
    
    F = [0 for h in range(depth)]

    sol=pricing_prob.solution.get_values(0,sum([len(C_set[j][f]) for j in get_leaf_parents(leaf,len(C_set)) for f in range(num_features)])-1)
                
    sol=np.array(sol)
        
    index = np.where(sol > 0.99)[0]
        
    for idx in index:
                
        var_name = pricing_prob.variables.get_names(int(idx))
        
        tmp=var_name.split("_")
        
        (i,v) = (int(tmp[-3]),int(tmp[-1]))
        
        F[int(tmp[-2])] = (i,v)
                        
    p = pattern(leaf,F,0,[],0) #target and score will be computed in the next function
            
    return p
            

def give_solution_type(prob): #return a string saying if the solution is integral, continuous or infeasible
    """ Compute the solution status of an already solved problem
    
    Input:
        prob (Cplex problem): already solved problem
        
    Output:
        status (string): status of the solution (can be infeasible, continuous or integer)
    """
    
    
    if "infeasible" in prob.solution.status[prob.solution.get_status()]:

        return "infeasible"
    
    else:
        
        for v in prob.variables.get_names():
            
            i = prob.solution.get_values(v)
            
            if ((float(i) <= round(i) - 0.01) or (float(i) >= round(i) + 0.01)):
                
                return "continuous"
            
        return "integer"
    