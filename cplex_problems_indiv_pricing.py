# -*- coding: utf-8 -*-
"""
Created on Wed Apr 25 09:58:57 2018

@author: Guillaume
"""

from learn_tree_funcs import get_left_leafs, get_right_leafs
from learn_tree_funcs import get_num_features, get_data_size, get_feature_value, get_target, get_leaf_parents, get_depth
import cplex

def create_variables_pricing(depth,master_prob,leaf,target,C_set,master_thresholds):
    
    var_names = []

    var_types = ""

    var_lb = []

    var_ub = []

    var_obj = []

    num_features = get_num_features()

    data_size = get_data_size()

    num_leafs = 2**depth

    num_nodes = num_leafs-1
    
    new_R = []
        
    for r in range(data_size): # On paper : x_{r}
        
        if get_target(r)==target:
            
            var_names.append("row_"+str(r))
            
            var_types += "B"
            
            var_lb.append(0)
            
            var_ub.append(1)
            
            new_R.append(r)
            
            var_obj.append(1)
            
    for i in range(num_features): # On paper : u_{i,h,v}
        
        for j in range(num_nodes):
            
            if j in get_leaf_parents(leaf,num_nodes):
                
                h = get_depth(j,num_nodes) - 1
            
                for v in range(len(C_set[i])):
                    
                    var_names.append("u_"+str(i)+"_"+str(h)+"_"+str(v))
                    
                    var_types += "B"
                    
                    var_lb.append(0)
                    
                    var_ub.append(1)
                    
                    if (j,i,v) in master_thresholds:
                    
                        var_obj.append(-master_prob.solution.get_dual_values("constraint_3_" + str(leaf) + "_" + str(j)+"_" + str(i)+"_" + str(v)))      
                        
                    else:
                        
                        var_obj.append(0)
                
    return var_names, var_types, var_lb, var_ub, var_obj, new_R
            
            
def create_rows_pricing(depth,leaf,C_set,new_R):
    
    row_names = []

    row_values = []

    row_right_sides = []

    row_senses = ""

    num_features = get_num_features()
        
    for h in range(depth): #constraint (7)
        
        col_names = ["u_"+str(i)+"_"+str(h)+"_"+str(v) for i in range(num_features) for v in range(len(C_set[i]))]

        col_values = [1 for i in range(num_features) for v in range(len(C_set[i]))]

        row_names.append("contraint_7_" + str(h))

        row_values.append([col_names,col_values])

        row_right_sides.append(1)

        row_senses = row_senses + "E"
        
    bin_l = bin(leaf)[2:].zfill(depth)
        
    for h in range(depth): # constraint(8)
        
        if bin_l[h]=='0':
            
            for r in new_R:
                
                col_names = ["row_"+str(r)]
                
                col_values = [1]
                
                for i in range(num_features):
                    
                    for v in range(len(C_set[i])):
                        
                        if get_feature_value(r,i) <= C_set[i][v]:
                            
                            col_names.append("u_"+str(i)+"_"+str(h)+"_"+str(v))
                            
                            col_values.append(-1)
                            
                row_names.append("contraint_8_" + str(h) + "_" +str(r))

                row_values.append([col_names,col_values])
        
                row_right_sides.append(0)
        
                row_senses = row_senses + "L"
                
        else:
            
            for r in new_R:
                
                col_names = ["row_"+str(r)]
                
                col_values = [1]
                
                for i in range(num_features):
                    
                    for v in range(len(C_set[i])):
                        
                        if get_feature_value(r,i) > C_set[i][v]:
                            
                            col_names.append("u_"+str(i)+"_"+str(h)+"_"+str(v))
                            
                            col_values.append(-1)
                            
                row_names.append("contraint_8_" + str(h) + "_" +str(r))

                row_values.append([col_names,col_values])
        
                row_right_sides.append(0)
        
                row_senses = row_senses + "L"
            
        
    return row_names, row_values, row_right_sides, row_senses
    

def construct_pricing_problem(depth,master_prob,leaf,target,master_thresholds,C_set):
        
    prob = cplex.Cplex()
    
    prob.objective.set_sense(prob.objective.sense.maximize)

    var_names, var_types, var_lb, var_ub, var_obj, new_R = create_variables_pricing(depth,master_prob,leaf,target,C_set,master_thresholds)
                    
    prob.variables.add(obj = var_obj, lb = var_lb, ub = var_ub, types = var_types, names = var_names)
    
    row_names, row_values, row_right_sides, row_senses = create_rows_pricing(depth,leaf,C_set,new_R)
    
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