# -*- coding: utf-8 -*- 
"""
Created on Wed Apr 18 09:58:55 2018

@author: Guillaume
"""

import regtrees2 as tr
from learn_tree_funcs import transform_data, read_file, write_file, scale_data, get_num_features, get_feature_value, get_data_size, get_target, get_leaf_parents, get_sorted_feature_values
from learn_tree_funcs import sget_children, get_left_node, get_right_node, obtain_targets2
from utility import init_rand_hash
from CG import obtain_depth
from collections import Counter
from pattern import pattern
from cplex_problems_indiv_pricing import obtain_targets
from heuristics import init_heur


def create_instance(inputfile,test=False):
    """ Create an instance from an input file
    
    Input:
        inputfile (string): file to be read
        test (bool): if True, return the dataframe (needed when testing)
        
    Output:
        tr.df (DataFrame, optional): dataframe with the data
    """
    
    read_file(inputfile)
   
    #scale_data()
    
    #transform_data()

    write_file(inputfile+".transformed")
   
    tr.df = tr.get_data(inputfile+".transformed")
    
    tr.df[tr.df.columns[-1]]=tr.df[tr.df.columns[-1]].astype('int')
    
    if test:
        
        return tr.df
        
        
def create_first_solution(inputdepth):
    """ Create the very first solution from a CART tree
    
    Input:
        inputdepth (integer): maximum depth
        
    Output:
        patterns_set (list of list of patterns): initial tree
        master_thresholds (list of triples): set of index corresponding to C_set
        TARGETS (list of floats): targets appearing in the problem
        C_set (list of list of list of floats): full thresholds
    """
    
    dt, TARGETS = tr.learnTrees_and_return_patterns(inputdepth)

    tr.get_code()
    
    num_leafs = 2**inputdepth
    
    num_nodes = num_leafs - 1
    
    data_size = get_data_size()
    
    C_set = compute_C_set(inputdepth)
        
    master_thresholds = get_feature_and_thresholds(dt,inputdepth)
            
    convert_thresholds_to_index(master_thresholds,C_set)
        
    patterns_set, R = [[] for l in range(num_leafs)], [[] for l in range(num_leafs)]
    
    for r in range(data_size): #compute rows
        
        bin_code = ""
        
        j = num_leafs/2 - 1
        
        for h in range(inputdepth):
                        
            triple = next(x for x in master_thresholds if x[0]==j)
            
            j, i, v =triple[0], triple[1], triple[2]
                        
            if get_feature_value(r,i) <= C_set[j][i][v]:
                
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
    """ Convert the thresholds from a CART tree to a list
    
    Input:
        dt (DecisionTreeClassifier): CART decision tree
        depth (integer): maximum depth of the tree
        
    Output:
        master_thresholds (list of triples): set of index corresponding to C_set
    """
    
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
    """ Convert the first version of master threshold into a new one with the correct index
    
    Input:
        master_thresholds (list of triples): set of index corresponding to C_set
        C_set (list of list of list of floats): full thresholds set
        
    Output:
        none (works in place)
    """
    
    for m in range(len(master_thresholds)):
        
        (j,i,v) = master_thresholds[m]
        
        new_v = 0
        
        if len(C_set[j][i])>1: #if not a categorical feature
        
            while new_v+1 < len(C_set[j][i]) and v >= (C_set[j][i][new_v] + C_set[j][i][new_v+1])/2:
                            
                new_v += 1
            
        master_thresholds[m] = (j,i,new_v)
    

def compute_C_set(depth):
    """ Compute the whole threshold set
    
    Input:
        depth (integer): maximum depth of the tree
        
    Output:
        C_set (list of list of list of floats): full thresholds set
    """
    
    num_features = get_num_features()
    
    C_set = [[[] for i in range(num_features)] for j in range(2**depth-1)]
    
    for j in range(2**depth -1):
    
        for i in range(num_features):
            
            feats = get_sorted_feature_values(i)
            
            for k in range(len(feats)-1):
                
                C_set[j][i].append((feats[k] + feats[k+1])/2.)
            
    return C_set

def restricted_C_set(C_set,patterns_set,depth):
    """ Compute the restricted thresholds set using homogeneous sampling (unused)
    
    Input:
        C_set (list of list of list of floats): full thresholds set
        patterns_set (list of list of patterns): initial tree
        depth (integer): maximum depth of the tree
        
    Output:
        new_C_set (list of list of list of floats): restricted thresholds set
        new_MT (list of triples): set of index corresponding to C_set
    """
    
    num_features = get_num_features()
    
    new_C_set = [[[] for i in range(num_features)] for j in range(2**depth-1)]
    
    for j in range(len(C_set)):
    
        for i in range(num_features):
            
            if len(C_set[j][i])<=6:
                
                cut=1
            
            elif len(C_set[j][i])<20:
                
                cut=4
            
            elif len(C_set[j][i])<100:
                
                cut=20
                
            elif len(C_set[j][i])<200:
                
                cut=40
                
            else:
                
                cut=100
            
            for v in range(len(C_set[j][i])):
                
                if (v+3)%cut==0:
                    
                    new_C_set[j][i].append(C_set[j][i][v])
                
    for l in range(len(patterns_set)):
        
        F = patterns_set[l][0].F
        
        parents = get_leaf_parents(l,len(C_set))
        
        for h in range(depth):
            
            (i,v) = F[h]
            
            if C_set[j][i][v] not in new_C_set[j][i]:
                
                new_C_set[j][i].append(C_set[j][i][v])
                
    for j in range(len(C_set)):
                
        for i in range(num_features):
        
            new_C_set[j][i].sort()
        
    new_MT = []
    
    num_leafs = len(patterns_set)
    
    for l in range(num_leafs):
        
        F = patterns_set[l][0].F
        
        parents = get_leaf_parents(l,num_leafs-1)
        parents.reverse()
        
        for h in range(len(F)):
            
            (i,v) = F[h]
            
            j = parents[h]
            
            v2 = new_C_set[j][i].index(C_set[j][i][v])
            
            F[h] = (i,v2)
            
            print(l,h,i,v2)
            
            new_MT.append((parents[h],i,v2))
            
    print('Unique values: '+str(sum([len(new_C_set[j2][z]) for j2 in range(len(C_set)) for z in range(num_features)])))
            
    return new_C_set, new_MT

def restricted_C_set2(C_set,patterns_set,depth): #compute the restricted C_set using information from CART trees
    """ Compute the restricteds threshold set using CART trees
    
    Input:
        C_set (list of list of list of floats): full thresholds set
        patterns_set (list of list of patterns): initial tree
        depth (integer): maximum depth of the tree
        
    Output:
        new_C_set (list of list of list of floats): restricted thresholds set
        new_MT (list of triples): set of index corresponding to C_set
    """
    
    num_features = get_num_features()
    
    new_C_set = [[[] for i in range(num_features)] for j in range(2**depth-1)]
    
    new_MT = []
    
    stop, count = 0, 0
    
    list_thr = [[] for j in range(2**depth-1)]
    
    max_iter=300
    
    while stop<max_iter:
        
        count += 1
        
        dt, TARGETS = tr.learnTrees_and_return_patterns(depth,sample=count)
                
        tree_thresholds = get_feature_and_thresholds(dt,depth)
                
        convert_thresholds_to_index(tree_thresholds,C_set)
                        
        for j in range(2**depth -1):
                    
            triple = next(x for x in tree_thresholds if x[0]==j)
            
            i, v = triple[1], triple[2]
                                        
            if (i,v) not in list_thr[j]:
                
                list_thr[j].append((i,v))
                
                if j==(2**(depth-1) - 1):

                    stop=0
                
            elif j==(2**(depth-1) - 1):
                
                stop+=1
                
    for j in range(2**depth-1):
        
        if j==(2**(depth-1) - 1):
            
            for k in Counter(list_thr[j]).most_common(150/(2**depth-1)):
                
                (i,v)=k[0]
                
                if C_set[j][i][v] not in new_C_set[j][i]:
                    
                    new_C_set[j][i].append(C_set[j][i][v])
                    
        else:
                
            for k in Counter(list_thr[j]).most_common(100/(2**depth-1)):
                
                (i,v)=k[0]
                
                if C_set[j][i][v] not in new_C_set[j][i]:
                    
                    new_C_set[j][i].append(C_set[j][i][v])
        
    num_leafs = len(patterns_set)
        
    for l in range(num_leafs):
        
        F = patterns_set[l][0].F
        
        parents = get_leaf_parents(l,len(C_set))
        parents.reverse()
        
        for h in range(depth):
            
            (i,v) = F[h]
            
            j = parents[h]
            
            if C_set[j][i][v] not in new_C_set[j][i]:
                
                new_C_set[j][i].append(C_set[j][i][v])
                
    for j in range(len(C_set)):
                
        for i in range(num_features):
        
            new_C_set[j][i].sort()
        
    for l in range(num_leafs):
        
        F = patterns_set[l][0].F
        
        parents = get_leaf_parents(l,num_leafs-1)
        parents.reverse()
        
        for h in range(len(F)):
            
            (i,v) = F[h]
            
            j = parents[h]
            
            v2 = new_C_set[j][i].index(C_set[j][i][v])
            
            F[h] = (i,v2)
                        
            new_MT.append((parents[h],i,v2))
            
    print('Unique values: '+str(sum([len(new_C_set[j2][z]) for j2 in range(len(C_set)) for z in range(num_features)])))
    
    print('Unique values at root node: '+str(sum([len(new_C_set[2**(depth-1) - 1][z]) for z in range(num_features)])))
            
    return new_C_set, new_MT

                
def initialize_global_values(TARGETS,inputdepth):
    """ Give important global values to some modules
    
    Input:
        TARGETS (list of floats): targets appearing in the problem
        inputdepth (integer): maximum depth of the tree
        
    Output:
        none
    """
    
    TARGETS.sort()
    obtain_depth(inputdepth) #give depth to the BaP_Node module
    obtain_targets2(TARGETS)
    obtain_targets(TARGETS)
    init_rand_hash(inputdepth,get_num_features())
    init_heur()
