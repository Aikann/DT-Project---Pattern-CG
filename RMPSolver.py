# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 10:25:53 2018

@author: Guillaume
"""

from cplex_problems_master import construct_master_problem, add_variable_to_master

def create_new_master(depth,patterns_set,master_thresholds):
    
    return construct_master_problem(depth,patterns_set,master_thresholds)

def solveRMP(prob):
    
    prob.solve()
    
def add_column(depth,prob,patterns_set,pattern_to_add,leaf,master_thresholds):
    
    return add_variable_to_master(depth,prob,patterns_set,pattern_to_add,leaf,master_thresholds)
    
def display_prob_lite(prob,side):
    
    if side == "primal":
        
        for i in prob.variables.get_names():
            
            print(i, prob.solution.get_values(i))
            
    else:
        
        for i in prob.linear_constraints.get_names():
            
            print(i, prob.solution.get_dual_values(i))