# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 10:12:37 2018

@author: Guillaume
"""

from RMPSolver import create_new_master
from CG import BaP_Node
import time
from utility import hash_pattern

def tree(TARGETS,patterns_set,best_solution_value,inputdepth,C_set,master_thresholds,timelimit):
    """ Core function to solve the problem
    
    Input:
        TARGETS (list of floats): targets appearing in the problem
        patterns_set (list of list of patterns): initial tree
        best_solution_value (integer): objective value of the initial tree
        inputdepth (integer): maximum depth of the tree
        C_set (list of list of list of floats): restricted thresholds set
        master_thresholds (list of triples): set of index corresponding to C_set
        timelimit (integer): time limit in seconds
        
    Output:
        final_tree (list of patterns): the final decision tree
    """
    
    prob=create_new_master(inputdepth,patterns_set,master_thresholds,C_set)
    
    H = [[0] for l in range(len(patterns_set))]
    
    for l in range(len(patterns_set)):
        
        for p in range(len(patterns_set[l])):
        
            H[l].append(hash_pattern(patterns_set[l][p]))
                            
    root_node=BaP_Node(patterns_set,prob,"",None,H,[],[],master_thresholds) #construct root node
            
    a=time.time()
    
    root_node.explore(C_set,timelimit)
    
    if root_node.solution_type == 'integer':
        
        print('Integer for LP')
    
    print("Full time : "+str(time.time()-a))
    
    print("Upper bound at root node : "+str(root_node.prob.solution.get_objective_value()))
    
    print("Number of columns: "+str(sum([len(root_node.patterns_set[l]) for l in range(2**inputdepth)])))
    
    UB = root_node.prob.solution.get_objective_value()
    
    if round(UB) - 1e-5 <= UB <= round(UB) + 1e-5:
        
        UB = int(round(UB))
        
    else:
        
        UB = int(UB)
    
        for i in root_node.prob.variables.get_names():
        
            root_node.prob.variables.set_types(i,"B")
            
        root_node.prob.solve()
        
        root_node.solution_type='integer'
        
        best_solution_value = root_node.prob.solution.get_objective_value()
                             
    print("Best solution: "+str(best_solution_value))
    
    print("Total time :"+str(time.time() - a))
        
    final_tree=[]
    
    for leaf in range(2**inputdepth):
        
        final_tree.append(next(root_node.patterns_set[leaf][pat] for pat in range(len(root_node.patterns_set[leaf])) if float(root_node.prob.solution.get_values("pattern_"+str(pat)+"_"+str(leaf)))>=0.99))

    return final_tree
    
    