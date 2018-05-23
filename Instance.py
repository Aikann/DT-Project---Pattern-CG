# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 09:58:55 2018

@author: Guillaume
"""

import regtrees2 as tr
from learn_tree_funcs import transform_data, read_file, write_file, scale_data, get_num_features, get_feature_value, get_data_size, get_target, get_leaf_parents, get_sorted_feature_values
import copy
from nodes_external_management import init_rand_hash
from BaP_Node import obtain_depth
from random import random
from collections import Counter
from pattern import pattern

def create_instance(inputfile):
    
    read_file(inputfile)
   
    scale_data()
    
    #transform_data()

    write_file(inputfile+".transformed")
   
    tr.df = tr.get_data(inputfile+".transformed")
    
def create_first_solution(inputdepth):
    
    targets = tr.learnTrees_and_return_patterns(inputdepth) #TODO;
    
    tr.get_code()
    
    return targets

def compute_C_set():
    
    num_features = get_num_features()
    
    C_set = [[] for i in range(num_features)]
    
    for i in range(num_features):
        
        feats = get_sorted_feature_values(i)
        
        for k in range(len(feats)-1):
            
            C_set[i].append((feats[k] + feats[k+1])/2.)
            
    return C_set

def basic_patterns(depth,C_set):
    
    data_size = get_data_size()
    
    num_leafs = 2**depth
    
    num_nodes = num_leafs - 1
        
    patterns_set, master_thresholds = [], []
    
    R = [r for r in range(data_size)]
    
    features = [get_feature_value(r,0) for r in range(data_size)]
    
    sorted_R = [r for y, r in sorted(zip(features, R))]
            
    features.sort()
        
    step = data_size/(num_leafs)
    
    for l in range(num_leafs):
        
        bin_l = bin(l)[2:].zfill(8)
        
        F = []
        
        for h in range(depth):
            
            k=0
            
            if bin_l[-h-1] == '0':
                                
                while features[step*(l+1)]==features[step*(l+1) - 1 - k]:
                    
                    print("Feature equality when constructing first solution")
                    
                    k=k+1
                                
                F.append((0,C_set[0].index((features[step*(l+1)]+features[step*(l+1) - 1 - k])/2)))
                                                        
            else:
                
                while features[step*(l)]==features[step*(l) - 1 - k]:
                    
                    print("Feature equality when constructing first solution")
                    
                    k=k+1
                
                F.append((0,C_set[0].index((features[step*(l)]+features[step*(l) - 1 - k])/2)))
                
        if l == num_leafs-1:
            
            R = copy.copy(sorted_R[step*l:])
            
        else:
                
            R = copy.copy(sorted_R[step*l:step*(l+1)])
        
        targets = [get_target(r) for r in R]
        
        pred = Counter(targets).most_common(1)[0][0]
            
        correct = sum([1 for r in R if get_target(r)==pred])
                
        F.reverse()
        
        p = pattern(l,F,correct,R,pred)
        
        patterns_set.append([p])
        
    for l in range(num_leafs):
        
        for h in range(depth):
            
            for v in range(len(C_set[0])):
                
                j = get_leaf_parents(l,num_nodes)[-h-1]
                
                if (j,0,v) not in master_thresholds:
                    
                    master_thresholds.append((j,0,v))
        
    return patterns_set, master_thresholds
        
        
                
def initialize_global_values(TARGETS,inputdepth,C_set):
    
    TARGETS.sort()
    obtain_depth(inputdepth) #give depth to the BaP_Node module
    init_rand_hash(inputdepth,get_num_features(),C_set)
