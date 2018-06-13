# -*- coding: utf-8 -*-
"""
Created on Wed Apr 25 09:58:57 2018

@author: Guillaume
"""

from learn_tree_funcs import get_left_leafs, get_right_leafs
from learn_tree_funcs import get_num_features, get_data_size, get_feature_value, get_target, get_leaf_parents, get_depth
import cplex
import numpy as np

def obtain_targets(T):
    
    global TARGETS    
    TARGETS = T

def create_variables_pricing(depth,leaf,target,C_set):
    
    var_names = []

    var_types = ""

    var_lb = []

    var_ub = []

    var_obj = []

    num_features = get_num_features()

    data_size = get_data_size()

    num_leafs = 2**depth

    num_nodes = num_leafs-1
        
    for j in range(num_nodes): # On paper : u_{i,h,v}
            
        if j in get_leaf_parents(leaf,num_nodes):
            
            h = get_depth(j,num_nodes) - 1
                        
            for i in range(num_features): 
            
                for v in range(len(C_set[j][i])):
                    
                    var_names.append("u_"+str(i)+"_"+str(h)+"_"+str(v))
                    
                    var_types += "B"
                    
                    var_lb.append(0)
                    
                    var_ub.append(1)
                    
                    var_obj.append(0)
       
    for r in range(data_size): # On paper : x_{r}
            
            var_names.append("row_"+str(r))
            
            var_types += "B"
            
            var_lb.append(0)
            
            var_ub.append(1)
                    
            var_obj.append(1)
                
    return var_names, var_types, var_lb, var_ub, var_obj
            
            
def create_rows_pricing(depth,leaf,C_set):
    
    row_names = []

    row_values = []

    row_right_sides = []

    row_senses = ""
    
    data_size = get_data_size()

    num_features = get_num_features()
    
    parents = get_leaf_parents(leaf,len(C_set))
            
    for h in range(depth): #constraint (7)
        
        j = parents[-h-1]
        
        col_names = ["u_"+str(i)+"_"+str(h)+"_"+str(v) for i in range(num_features) for v in range(len(C_set[j][i]))]

        col_values = [1 for i in range(num_features) for v in range(len(C_set[j][i]))]

        row_names.append("contraint_7_" + str(h))

        row_values.append([col_names,col_values])

        row_right_sides.append(1)

        row_senses = row_senses + "E"
        
    bin_l = bin(leaf)[2:].zfill(depth)
        
    for h in range(depth): # constraint(8)
        
        j = parents[-1-h]
        
        if bin_l[h]=='0':
            
            for r in range(data_size):
                
                col_names = ["row_"+str(r)]
                
                col_values = [1]
                
                for i in range(num_features):
                    
                    for v in range(len(C_set[j][i])):
                        
                        if get_feature_value(r,i) <= C_set[j][i][v]:
                            
                            col_names.append("u_"+str(i)+"_"+str(h)+"_"+str(v))
                            
                            col_values.append(-1)
                            
                row_names.append("contraint_8_" + str(h) + "_" +str(r))

                row_values.append([col_names,col_values])
        
                row_right_sides.append(0)
        
                row_senses = row_senses + "L"
                
        else:
            
            for r in range(data_size):
                
                col_names = ["row_"+str(r)]
                
                col_values = [1]
                
                for i in range(num_features):
                    
                    for v in range(len(C_set[j][i])):
                        
                        if get_feature_value(r,i) > C_set[j][i][v]:
                            
                            col_names.append("u_"+str(i)+"_"+str(h)+"_"+str(v))
                            
                            col_values.append(-1)
                            
                row_names.append("contraint_8_" + str(h) + "_" +str(r))

                row_values.append([col_names,col_values])
        
                row_right_sides.append(0)
        
                row_senses = row_senses + "L"
                
        for r in range(data_size):
            
            col_names, col_values = [], []
            
            for h in range(depth):
                
                j = parents[-h-1]
        
                if bin_l[h]=='0':
                                                                                    
                    for i in range(num_features):
                        
                        for v in range(len(C_set[j][i])):
                            
                            if get_feature_value(r,i) <= C_set[j][i][v]:
                                
                                col_names.append("u_"+str(i)+"_"+str(h)+"_"+str(v))
                                
                                col_values.append(1)
                                
                else:
                    
                    for i in range(num_features):
                        
                        for v in range(len(C_set[j][i])):
                            
                            if get_feature_value(r,i) > C_set[j][i][v]:
                                
                                col_names.append("u_"+str(i)+"_"+str(h)+"_"+str(v))
                                
                                col_values.append(1)
                                
            col_names.append("row_"+str(r))
            
            col_values.append(-1)
                                
            row_names.append("constraint_9_" + str(r))

            row_values.append([col_names,col_values])
    
            row_right_sides.append(depth-1)
    
            row_senses = row_senses + "L"
            
    #TODO; modify the following constraint with the new C_set
    """
    for i in range(num_features):
        
        for v in range(len(C_set[j][i])):
            
            col_names = ["u_"+str(i)+"_"+str(h)+"_"+str(v) for h in range(depth)]
            
            col_values = [1 for h in range(depth)]
            
            row_names.append("constraint_10_" + str(i) +"_"+str(v))

            row_values.append([col_names,col_values])
    
            row_right_sides.append(1)
    
            row_senses = row_senses + "L"
    """            
        
    return row_names, row_values, row_right_sides, row_senses
    

def construct_pricing_problem(depth,leaf,target,C_set):
            
    prob = cplex.Cplex()
    
    prob.objective.set_sense(prob.objective.sense.maximize)

    var_names, var_types, var_lb, var_ub, var_obj = create_variables_pricing(depth,leaf,target,C_set)
                    
    prob.variables.add(obj = var_obj, lb = var_lb, ub = var_ub, types = var_types, names = var_names)
    
    row_names, row_values, row_right_sides, row_senses = create_rows_pricing(depth,leaf,C_set)
    
    prob.linear_constraints.add(lin_expr = row_values, senses = row_senses, rhs = row_right_sides, names = row_names)
    
    prob.parameters.emphasis.mip.set(1)

    #prob.parameters.advance.set(2)
    
    #prob.parameters.mip.strategy.branch.set(1)
    #prob.parameters.mip.strategy.backtrack.set(1.0)
    #prob.parameters.mip.strategy.nodeselect.set(2)
    prob.parameters.mip.strategy.variableselect.set(-1)
    #prob.parameters.mip.strategy.bbinterval.set(0)
    #prob.parameters.mip.strategy.rinsheur.set(50)
    #prob.parameters.mip.strategy.lbheur.set(1)
    #prob.parameters.mip.strategy.probe.set(3)

    #prob.parameters.preprocessing.presolve.set(1)
                    
    prob.set_log_stream(None)
    prob.set_error_stream(None)
    prob.set_warning_stream(None)
    prob.set_results_stream(None)
    
    return prob
    
def update_pricing(depth,prev_pricing,leaf,target,master_prob,master_thresholds,C_set):
    
    for r in range(get_data_size()):
        
        prev_pricing.objective.set_linear("row_"+str(r),-master_prob.solution.get_dual_values("row_constraint_"+str(r)) + int(get_target(r)==TARGETS[target]))
    
    parents = get_leaf_parents(leaf,2**depth-1)
                                                                        
    for (j,i,v) in master_thresholds:
        
        if j in parents:
        
            h = get_depth(j,2**depth - 1) - 1
                        
            prev_pricing.objective.set_linear("u_"+str(i)+"_"+str(h)+"_"+str(v),-master_prob.solution.get_dual_values("constraint_3_" + str(leaf) + "_" + str(j)+"_" + str(i)+"_" + str(v)))
                            
    return prev_pricing