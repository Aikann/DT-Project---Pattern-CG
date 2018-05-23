# -*- coding: utf-8 -*-
"""
Created on Wed Apr 11 15:36:08 2018

@author: Guillaume
"""

from learn_tree_funcs import get_num_targets, get_left_leafs, get_right_leafs, get_leaf_parents, get_depth
from learn_tree_funcs import get_num_features, get_data_size, get_min_value, get_max_value, get_feature_value, get_target
import cplex


def add_variable_to_master(depth,prob,prev_patterns_set,pattern_to_add,leaf,master_thresholds):
        
    num_leafs = 2**depth

    num_nodes = num_leafs-1
                        
    var_types, var_lb, var_ub, var_obj, var_names = "", [], [], [], []
        
    my_columns = [[[],[]]]
            
    p=pattern_to_add
                            
    var_types += "C"

    var_lb.append(0)

    var_ub.append(cplex.infinity)

    var_obj.append(p.c)
    
    var_names.append("pattern_" + str(len(prev_patterns_set)-1) + "_" + str(leaf))
            
    my_columns[0][0].append("constraint_2_"+str(leaf))
    
    my_columns[0][1].append(1)
                    
    path = get_leaf_parents(leaf,num_nodes)
    
    for h in range(depth):
        
        (i,v) = p.F[h]
        
        j = path[-h-1]
        
        if "rho_" + str(j) + "_" + str(i) + "_" + str(v) not in prob.variables.get_names(): #add rho if it is a new one
                    
            var_names.append("rho_" + str(j) + "_" + str(i) + "_" + str(v))
            
            var_types += "C"
    
            var_lb.append(-cplex.infinity)
        
            var_ub.append(cplex.infinity)
        
            var_obj.append(0)
            
            my_columns.append([[],[]])
            
            for l in range(num_leafs):
            
                my_columns[1][0].append("constraint_3_" + str(l) + "_" + str(j)+"_" + str(i)+"_" + str(v))
        
                my_columns[1][1].append(-1)
                        
            # add empty constraints
            
            for l in range(num_leafs):
                
                col_names = []
                
                col_values = []
                            
                row_names=["constraint_3_" + str(l) + "_" + str(j)+"_" + str(i)+"_" + str(v)]
            
                row_right_sides = [0]
            
                row_values=[[col_names,col_values]]
    
                row_senses = "E"
                
                prob.linear_constraints.add(lin_expr = row_values, senses = row_senses, rhs = row_right_sides, names = row_names)
                                
        my_columns[0][0].append("constraint_3_" + str(leaf) + "_" + str(j)+"_" + str(i)+"_" + str(v))
        
        my_columns[0][1].append(1)
    
    prob.variables.add(obj = var_obj, lb = var_lb, ub = var_ub, types = var_types, columns = my_columns, names = var_names)
            
    prob.set_problem_type(0)
    
    return prob
    
    
def create_variables_CG(depth,patterns_set,master_thresholds):
    
    var_value = 0

    var_names = []

    var_types = ""

    var_lb = []

    var_ub = []

    var_obj = []

    num_leafs = 2**depth

    # On the paper: rho_{i,j,v}

    for (j,i,v) in master_thresholds:

        var_names.append("rho_" + str(j) + "_" + str(i) + "_" + str(v))

        var_types = var_types + "C"

        var_lb.append(-cplex.infinity)

        var_ub.append(cplex.infinity)

        var_obj.append(0)

        var_value = var_value + 1

    # On the paper : x_{p,l}
    
    for l in range(num_leafs):
        
        for p in range(len(patterns_set[l])):
            
            var_names.append("pattern_"+str(p)+"_"+str(l))
            
            var_types = var_types + "C"

            var_lb.append(0)

            var_ub.append(cplex.infinity)

            var_obj.append(patterns_set[l][p].c)

            var_value = var_value + 1


    return var_names, var_types, var_lb, var_ub, var_obj


def create_rows_CG(depth,patterns_set,master_thresholds):

    row_names = []

    row_values = []

    row_right_sides = []

    row_senses = ""

    num_leafs = 2**depth

    num_nodes = num_leafs-1
    
    for l in range(num_leafs): #constraint (2)
        
        col_names = ["pattern_"+str(p)+"_"+str(l) for p in range(len(patterns_set[l]))]
        
        col_values = [1 for p in range(len(patterns_set[l]))]
        
        row_names.append("constraint_2_" + str(l))
                
        row_right_sides.append(1)
        
        row_values.append([col_names,col_values])

        row_senses = row_senses + "E"
    
    for l in range(num_leafs): #constraint (3)
        
        for (j,i,v) in master_thresholds:
                
                d = get_depth(j,num_nodes) - 1
                
                col_names = ["pattern_"+str(p)+"_"+str(l) for p in range(len(patterns_set[l])) if patterns_set[l][p].F[d]==(i,v)]
                
                col_values = [1 for p in range(len(patterns_set[l])) if patterns_set[l][p].F[d]==(i,v)]
                
                col_names.append("rho_" + str(j) + "_" + str(i) + "_" + str(v))
                
                col_values.append(-1)
                
                row_names.append("constraint_3_" + str(l) + "_" + str(j)+"_" + str(i)+"_" + str(v))
                
                row_right_sides.append(0)
                
                row_values.append([col_names,col_values])

                row_senses = row_senses + "E"
                                    
                
    return row_names, row_values, row_right_sides, row_senses


def construct_master_problem(depth,patterns_set,master_thresholds):
        
    prob = cplex.Cplex()
    
    prob.objective.set_sense(prob.objective.sense.maximize)

    var_names, var_types, var_lb, var_ub, var_obj = create_variables_CG(depth,patterns_set,master_thresholds)
    
    prob.variables.add(obj = var_obj, lb = var_lb, ub = var_ub, types = var_types, names = var_names)

    row_names, row_values, row_right_sides, row_senses = create_rows_CG(depth,patterns_set,master_thresholds)
    
    prob.linear_constraints.add(lin_expr = row_values, senses = row_senses, rhs = row_right_sides, names = row_names)
            
    prob.set_problem_type(0) #tell cplex this is a LP, not a MILP
    
    prob.set_log_stream(None)
    prob.set_error_stream(None)
    prob.set_warning_stream(None)
    prob.set_results_stream(None)
    
    return prob