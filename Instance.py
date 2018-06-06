# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 09:58:55 2018

@author: Guillaume
"""

import regtrees2 as tr
from learn_tree_funcs import transform_data, read_file, write_file, scale_data, get_num_features, get_feature_value, get_data_size, get_target, get_leaf_parents, get_sorted_feature_values
from learn_tree_funcs import sget_children, get_left_node, get_right_node
from nodes_external_management import init_rand_hash
from BaP_Node import obtain_depth
from collections import Counter
from pattern import pattern
from cplex_problems_indiv_pricing import obtain_targets
import numpy as np

def create_instance(inputfile):
    
    read_file(inputfile)
   
    scale_data()
    
    #transform_data()

    write_file(inputfile+".transformed")
   
    tr.df = tr.get_data(inputfile+".transformed")
    
def create_first_solution(inputdepth):
    
    dt, TARGETS = tr.learnTrees_and_return_patterns(inputdepth)

    tr.get_code()
    
    num_leafs = 2**inputdepth
    
    num_nodes = num_leafs - 1
    
    data_size = get_data_size()
    
    C_set = compute_C_set()
        
    master_thresholds = get_feature_and_thresholds(dt,inputdepth)
            
    convert_thresholds_to_index(master_thresholds,C_set)
        
    patterns_set, R = [[] for l in range(num_leafs)], [[] for l in range(num_leafs)]
    
    for r in range(data_size): #compute rows
        
        bin_code = ""
        
        j = num_leafs/2 - 1
        
        for h in range(inputdepth):
                        
            triple = next(x for x in master_thresholds if x[0]==j)
            
            i, v = triple[1], triple[2]
                        
            if get_feature_value(r,i) <= C_set[i][v]:
                
                bin_code += "0"
                
                j = get_left_node(j,num_nodes)
                
            else:
                
                bin_code += "1"
                
                j = get_right_node(j,num_nodes)
                
        leaf = int(bin_code,2)
        
        R[leaf].append(r)
        
    for l in range(num_leafs): #compute patterns
        
        F = []
                
        for j in get_leaf_parents(l,num_nodes): #compute F_vector
            
            triple = next(x for x in master_thresholds if x[0]==j)
            
            F.append((triple[1],triple[2]))
            
        F.reverse()
        
        targets = [get_target(r) for r in R[l]]
    
        try:
            
            pred = Counter(targets).most_common(1)[0][0]
            
        except(IndexError): #empty list
            
            pred = 0
                
        c = sum([1 for r in R[l] if get_target(r)==pred])
        
        p = pattern(l,F,c,R[l],pred)
        
        patterns_set[l].append(p)
            
    return patterns_set, master_thresholds, TARGETS, C_set
    
    
def get_feature_and_thresholds(dt,depth):
    
    num_leafs = 2**depth
    
    num_nodes = num_leafs - 1
    
    master_thresholds = []
    
    sklearn_j, real_j = [0], [num_leafs/2 - 1]
    
    while len(sklearn_j)>0:
        
        i, v = dt.tree_.feature[sklearn_j[0]], dt.tree_.threshold[sklearn_j[0]]
        
        if i==-2 and v==-2:
            
            master_thresholds.append((real_j[0],0,0))
            
        else:
            
            master_thresholds.append((real_j[0],i,v))
            
        (sk_child0,sk_child1) = sget_children(dt,sklearn_j[0])
        
        if get_left_node(real_j[0],num_nodes) != -1: #if not a leaf
            
            sklearn_j.append(sk_child0)
            
            real_j.append(get_left_node(real_j[0],num_nodes))
            
        if get_right_node(real_j[0],num_nodes) != -1: #if not a leaf
            
            sklearn_j.append(sk_child1)
            
            real_j.append(get_right_node(real_j[0],num_nodes))
                
        del sklearn_j[0]
        del real_j[0]
        
    return master_thresholds
        
        
def convert_thresholds_to_index(master_thresholds,C_set):
    
    for m in range(len(master_thresholds)):
        
        (j,i,v) = master_thresholds[m]
        
        new_v = 0
        
        while v >= (C_set[i][new_v] + C_set[i][new_v+1])/2:
            
            new_v += 1
            
        master_thresholds[m] = (j,i,new_v)
    

def compute_C_set():
    
    num_features = get_num_features()
    
    C_set = [[] for i in range(num_features)]
    
    for i in range(num_features):
        
        feats = get_sorted_feature_values(i)
        
        for k in range(len(feats)-1):
            
            C_set[i].append((feats[k] + feats[k+1])/2.)
            
    return C_set

def restricted_C_set(C_set,patterns_set):
    
    num_features = get_num_features()
    
    new_C_set = [[] for i in range(num_features)]
    
    for i in range(num_features):
        
        if len(C_set[i])<=6:
            
            cut=1
        
        elif len(C_set[i])<20:
            
            cut=4
        
        elif len(C_set[i])<100:
            
            cut=20
            
        elif len(C_set[i])<200:
            
            cut=40
            
        else:
            
            cut=100
        
        for v in range(len(C_set[i])):
            
            if (v+3)%cut==0:
                
                new_C_set[i].append(C_set[i][v])
                
    for l in range(len(patterns_set)):
        
        F = patterns_set[l][0].F
        
        for (i,v) in F:
            
            if C_set[i][v] not in new_C_set[i]:
                
                new_C_set[i].append(C_set[i][v])
                
    for i in range(num_features):
        
        new_C_set[i].sort()
        
    new_MT = []
    
    num_leafs = len(patterns_set)
    
    for l in range(num_leafs):
        
        F = patterns_set[l][0].F
        
        parents = get_leaf_parents(l,num_leafs-1)
        parents.reverse()
        
        for h in range(len(F)):
            
            (i,v) = F[h]
            
            v2 = new_C_set[i].index(C_set[i][v])
            
            F[h] = (i,v2)
            
            new_MT.append((parents[h],i,v2))
            
    print('Unique values: '+str(sum([len(new_C_set[z]) for z in range(num_features)])))
            
    return new_C_set, new_MT
                    
def empty_patterns(depth):
    
    dt, TARGETS = tr.learnTrees_and_return_patterns(depth)

    tr.get_code()
    
    num_leafs = 2**depth
    
    num_nodes = num_leafs - 1
        
    C_set = compute_C_set()
    
    patterns_set = [[] for l in range(num_leafs)]
    
    for l in range(num_leafs):
        
        F = [(0,0) for h in range(depth)]
        
        p = pattern(l,F,0,[],0)
        
        patterns_set[l].append(p)
        
    master_thresholds = [(j,0,0) for j in range(num_nodes)]
    
    return patterns_set, master_thresholds, TARGETS, C_set

                
def initialize_global_values(TARGETS,inputdepth,C_set):
    
    TARGETS.sort()
    obtain_depth(inputdepth) #give depth to the BaP_Node module
    obtain_targets(TARGETS)
    init_rand_hash(inputdepth,get_num_features(),C_set)
