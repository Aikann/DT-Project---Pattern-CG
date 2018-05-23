# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 11:08:04 2018

@author: Guillaume
"""

from cplex_problems_indiv_pricing import construct_pricing_problem
from nodes_external_management import extract_pattern_pricing, color_leaf
import matplotlib.pyplot as plt
from learn_tree_funcs import get_num_targets
from RMPSolver import display_prob_lite

def avoid_method(depth):
    
    global avoid

    avoid =[[False for t in range(get_num_targets())] for l in range(2**depth)]

def solve_pricing_given_leaf_and_target(depth,prob,leaf,target,branch_var,branch_index,ID,master_thresholds,C_set):#return a tuple (segments, obj_value).
                         
    pricing_prob = construct_pricing_problem(depth,prob,leaf,target,master_thresholds,C_set)
                    
    pricing_prob.solve()
    
#try:
        
    obj_value = pricing_prob.solution.get_objective_value()
        
    obj_value = obj_value - prob.solution.get_dual_values("constraint_2_" + str(leaf))
                    
    pattern = extract_pattern_pricing(pricing_prob,leaf,depth,C_set)
    
    pattern.add_missing_rows(depth,C_set)
    
#except:
        
    #pattern, obj_value = [], float('-inf')
        
    return pattern, obj_value


def solve_pricing(depth,prob,patterns_set,branch_var,branch_index,ID,master_thresholds,C_set,pricing_method): #return a triple (segments_to_be_added, convergence, min(red_cost))
    
    from BaP_Node import count_iter
    
    num_leafs = len(patterns_set)
            
    patterns_to_be_added, obj_values = [], []
    
    if pricing_method==1:
    
        for l in range(num_leafs):
            
            for t in range(get_num_targets()):
            
                pattern, value = solve_pricing_given_leaf_and_target(depth,prob,l,t,branch_var,branch_index,ID,master_thresholds,C_set)
                
                patterns_to_be_added.append(pattern)
                
                obj_values.append(value)
                
                if -500 < value < 500:
                
                    plt.scatter(count_iter,value,color=color_leaf(l))
                
                    plt.pause(0.01)
                            
                print("Reduced cost for leaf "+str(l)+" :",str(value))
                
                #print(pattern)
                                
    return patterns_to_be_added, ((max(obj_values) < 0.01) and (pricing_method==1)), max(obj_values)

