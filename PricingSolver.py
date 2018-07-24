# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 11:08:04 2018

@author: Guillaume
"""

from cplex_problems_indiv_pricing import construct_pricing_problem, update_pricing
from utility import extract_pattern_pricing
from learn_tree_funcs import get_num_targets
import time
import numpy as np

def avoid_method(depth):
    """ Initialize a global list to perform CG more efficiently
    
    Input:
        depth (integer): maximum depth of the tree
        
    Output:
        none
    """
    
    global avoid

    avoid = np.array([[0 for t in range(get_num_targets())] for l in range(2**depth)])
    
def init_pricing_probs(depth,C_set):
    """ Initialize a global list containting the integer programs for the pricing
    
    Input:
        depth (integer): maximum depth of the tree
        C_set (list of list of list of floats): restricted thresholds set
        
    Output:
        none
    """
    
    global pricing_probs
    
    num_leafs = 2**depth
    
    num_targets = get_num_targets()
    
    pricing_probs = [[] for l in range(num_leafs)]
    
    for l in range(num_leafs):
    
        for t in range(num_targets):
            
            prob = construct_pricing_problem(depth,l,t,C_set)
            
            pricing_probs[l].append(prob)

def solve_pricing_given_leaf_and_target(depth,master_prob,leaf,target,master_thresholds,C_set):#return a tuple (segments, obj_value).
    """ Solve one given pricing problem
    
    Input:
        depth (integer): maximum depth of the tree
        master_prob (Cplex problem): current master problem
        leaf (integer): leaf of the pricing to be solved
        target (integer): target index of the target of the pricing to be solved
        master_thresholds (list of triples): set of index corresponding to C_set
        C_set (list of list of list of floats): restricted thresholds set
        
    Output:
        pattern (pattern): solution found by Cplex
        obj_value (float): objective value found by Cplex
    """
    
    
    global pricing_probs
    
    a=time.time()
    
    pricing_prob = update_pricing(depth,pricing_probs[leaf][target],leaf,target,master_prob,master_thresholds,C_set)
                
    print("Time constructing: "+str(time.time()-a))
    
    a=time.time()
                    
    pricing_prob.solve()
    
    print("Time solving: "+str(time.time()-a))
            
    obj_value = pricing_prob.solution.get_objective_value()
        
    obj_value = obj_value - master_prob.solution.get_dual_values("constraint_2_" + str(leaf))
                        
    pattern = extract_pattern_pricing(pricing_prob,leaf,depth,C_set)
            
    pattern.add_missing_rows(depth,C_set)
    
    pattern.pred_target()
                                
    return pattern, obj_value


def solve_pricing(depth,prob,master_thresholds,C_set):
    """ Solve all pricing problems
    
    Input:
        depth (integer): maximum depth of the tree
        prob (Cplex problem): current master problem
        master_thresholds (list of triples): set of index corresponding to C_set
        C_set (list of list of list of floats): restricted thresholds set
        
    Output:
        patterns_to_be_added (list of patterns): patterns found by the different pricing problems
        convergence (bool): certificate of optimality
        max(obj_values) (float): maximum reduced cost in patterns_to_be_added
        interesting_leaves (list of integers): leaves to be considered at the next iteration
    """    
    
    global avoid
    
    num_leafs = 2**depth
    
    interesting_leaves = []
            
    patterns_to_be_added, obj_values = [], []
        
    for l in range(num_leafs):
        
        for t in range(get_num_targets()):
            
            if avoid[l][t] > 10:
                
                avoid[l][t] = 0
                
            elif avoid[l][t] >=1:
                
                avoid[l][t] += 1
                
            else:
            
                pattern, value = solve_pricing_given_leaf_and_target(depth,prob,l,t,master_thresholds,C_set)
                
                patterns_to_be_added.append(pattern)
                
                obj_values.append(value)
                
                if value > 0.001:
                    
                    interesting_leaves.append(l)
                    
                if value <= 0.001:
                    
                    avoid[l][t] += 1
                    
                else:
                    
                    avoid[l][t] = 0
                                 
                print("Reduced cost for leaf "+str(l)+", target index "+str(t)+" :",str(value))
                            
            cv_proof=True
    
    if np.all(avoid < 2): #check if the pricing has been solved for every (leaf,target)
        
        cv_proof = True
        
    else:
        
        cv_proof = False
        
        if max(obj_values) < 0.01: #if it seems we converged
            
            avoid.fill(0) #solve all pricings at the next iteration
                      
    return patterns_to_be_added, ((max(obj_values) < 0.001) and (cv_proof)), max(obj_values), interesting_leaves

