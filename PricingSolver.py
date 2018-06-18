# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 11:08:04 2018

@author: Guillaume
"""

from cplex_problems_indiv_pricing import construct_pricing_problem, update_pricing
from nodes_external_management import extract_pattern_pricing, color_leaf
import matplotlib.pyplot as plt
from learn_tree_funcs import get_num_targets, get_target
from RMPSolver import display_prob_lite
import time
import numpy as np

def avoid_method(depth):
    
    global avoid

    avoid = np.array([[0 for t in range(get_num_targets())] for l in range(2**depth)])
    
def init_pricing_probs(depth,C_set):
    
    global pricing_probs
    
    num_leafs = 2**depth
    
    num_targets = get_num_targets()
    
    pricing_probs = [[] for l in range(num_leafs)]
    
    for l in range(num_leafs):
    
        for t in range(num_targets):
            
            prob = construct_pricing_problem(depth,l,t,C_set)
            
            pricing_probs[l].append(prob)

def solve_pricing_given_leaf_and_target(depth,master_prob,leaf,target,branch_var,branch_index,ID,master_thresholds,C_set):#return a tuple (segments, obj_value).
    
    global pricing_probs
    
    a=time.time()
    
    pricing_prob = update_pricing(depth,pricing_probs[leaf][target],leaf,target,master_prob,master_thresholds,C_set)
                
    print("Time constructing: "+str(time.time()-a))
    
    a=time.time()
                    
    pricing_prob.solve()
    
    print("Time solving: "+str(time.time()-a))
    
#try:
        
    obj_value = pricing_prob.solution.get_objective_value()
        
    obj_value = obj_value - master_prob.solution.get_dual_values("constraint_2_" + str(leaf))
    
    a=time.time()
                    
    pattern = extract_pattern_pricing(pricing_prob,leaf,depth,C_set)
    
    print("Time extracting: "+str(time.time()-a))
    
    a=time.time()
    
    pattern.add_missing_rows(depth,C_set)
    
    pattern.pred_target()
        
    print("Time completing: "+str(time.time()-a))
    
    #print(pattern)
    
#except:
        
    #pattern, obj_value = [], float('-inf')
        
    return pattern, obj_value


def solve_pricing(depth,prob,patterns_set,branch_var,branch_index,ID,master_thresholds,C_set,pricing_method): #return a triple (segments_to_be_added, convergence, min(red_cost))
    
    from BaP_Node import count_iter
    
    global avoid
    
    num_leafs = len(patterns_set)
    
    interesting_leaves = []
            
    patterns_to_be_added, obj_values = [], []
    
    if pricing_method==1:
    
        for l in range(num_leafs):
            
            for t in range(get_num_targets()):
                
                if avoid[l][t] > 10:
                    
                    avoid[l][t] = 0
                    
                elif avoid[l][t] >=1:
                    
                    avoid[l][t] += 1
                    
                else:
                
                    pattern, value = solve_pricing_given_leaf_and_target(depth,prob,l,t,branch_var,branch_index,ID,master_thresholds,C_set)
                    
                    patterns_to_be_added.append(pattern)
                    
                    obj_values.append(value)
                    
                    if value > 0.001:
                        
                        interesting_leaves.append(l)
                        
                    if value <= 0.001:
                        
                        avoid[l][t] += 1
                        
                    else:
                        
                        avoid[l][t] = 0
                        
                        """
                        plt.figure(2)
                        if -500 < value:
                        
                            plt.scatter(count_iter,value,color=color_leaf(l,t,depth))
                        
                            plt.pause(0.0001)
                        """                
                    print("Reduced cost for leaf "+str(l)+", target index "+str(t)+" :",str(value))
                    
                    #print(pattern)
                
                cv_proof=True
        
        if np.all(avoid < 2): #check if the pricing has been solved for every (leaf,target)
            
            cv_proof = True
            
        else:
            
            cv_proof = False
            
            if max(obj_values) < 0.01: #if it seems we converged
                
                avoid.fill(0) #solve all pricings at the next iteration
                      
    return patterns_to_be_added, ((max(obj_values) < 0.001) and (cv_proof)), max(obj_values), interesting_leaves

