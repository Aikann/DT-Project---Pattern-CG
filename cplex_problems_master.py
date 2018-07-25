# -*- coding: utf-8 -*- 
"""
Created on Wed Apr 11 15:36:08 2018

@author: Guillaume
"""

from learn_tree_funcs import get_leaf_parents, get_depth
from learn_tree_funcs import get_data_size
import cplex


def add_variable_to_master(depth,prob,prev_patterns_set,pattern_to_add):
        
    num_leafs = 2**depth

    num_nodes = num_leafs-1
                        
    var_types, var_lb, var_ub, var_obj, var_names = "", [], [], [], []
        
    my_columns = [[[],[]]]
            
    p=pattern_to_add
    
    leaf = p.leaf
                            
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
                                          
        my_columns[0][0].append("constraint_3_" + str(leaf) + "_" + str(j)+"_" + str(i)+"_" + str(v))
        
        my_columns[0][1].append(1)
        
    for r in p.R:
        
        my_columns[0][0].append("row_constraint_"+str(r))
        
        my_columns[0][1].append(1)
            
    prob.variables.add(obj = var_obj, lb = var_lb, ub = var_ub, types = var_types, columns = my_columns, names = var_names)
            
    prob.set_problem_type(0)
    
    return prob
    
    
def create_variables_CG(depth,patterns_set,C_set):
    
    var_value = 0

    var_names = []

    var_types = ""

    var_lb = []

    var_ub = []

    var_obj = []

    num_leafs = 2**depth
    
    num_nodes = num_leafs - 1

    # On the paper: rho_{i,j,v}
    
    for j in range(num_nodes):

        for i in range(len(C_set[j])):
            
            for v in range(len(C_set[j][i])):
    
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


def create_rows_CG(depth,patterns_set,master_thresholds,C_set):

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
        
    for l in range(num_leafs):
        
        parents = get_leaf_parents(l,num_nodes)
    
        for j in parents:
                
            for i in range(len(C_set[j])):
                
                for v in range(len(C_set[j][i])):
                    
                    if (j,i,v) in master_thresholds:
                    
                        d = get_depth(j,num_nodes) - 1
                        
                        col_names = ["pattern_"+str(p)+"_"+str(l) for p in range(len(patterns_set[l])) if patterns_set[l][p].F[d]==(i,v)]
                        
                        col_values = [1 for p in range(len(patterns_set[l])) if patterns_set[l][p].F[d]==(i,v)]
                        
                    else:
                        
                        col_names, col_values = [], []
                    
                    col_names.append("rho_" + str(j) + "_" + str(i) + "_" + str(v))
                    
                    col_values.append(-1)
                    
                    row_names.append("constraint_3_" + str(l) + "_" + str(j)+"_" + str(i)+"_" + str(v))
                    
                    row_right_sides.append(0)
                    
                    row_values.append([col_names,col_values])
    
                    row_senses = row_senses + "E"
                    
    for r in range(get_data_size()):
        
        col_names = ["pattern_"+str(p)+"_"+str(l) for l in range(num_leafs) for p in range(len(patterns_set[l])) if r in patterns_set[l][p].R]
        
        col_values = [1 for l in range(num_leafs) for p in range(len(patterns_set[l])) if r in patterns_set[l][p].R]
        
        row_names.append("row_constraint_"+str(r))
                    
        row_right_sides.append(1)
        
        row_values.append([col_names,col_values])

        row_senses = row_senses + "E"
                                    
                
    return row_names, row_values, row_right_sides, row_senses


def construct_master_problem(depth,patterns_set,master_thresholds,C_set):
        
    prob = cplex.Cplex()
    
    prob.objective.set_sense(prob.objective.sense.maximize)

    var_names, var_types, var_lb, var_ub, var_obj = create_variables_CG(depth,patterns_set,C_set)
    
    prob.variables.add(obj = var_obj, lb = var_lb, ub = var_ub, types = var_types, names = var_names)

    row_names, row_values, row_right_sides, row_senses = create_rows_CG(depth,patterns_set,master_thresholds,C_set)
    
    prob.linear_constraints.add(lin_expr = row_values, senses = row_senses, rhs = row_right_sides, names = row_names)
            
    prob.set_problem_type(0) #tell cplex this is a LP, not a MILP
    
    prob.set_log_stream(None)
    prob.set_error_stream(None)
    prob.set_warning_stream(None)
    prob.set_results_stream(None)
    
    return prob