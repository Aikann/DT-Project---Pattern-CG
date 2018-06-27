# -*- coding: utf-8 -*-
"""
Created on Tue May 29 09:47:19 2018

@author: Guillaume
"""

from pattern import pattern
from learn_tree_funcs import get_leaf_parents, get_num_features, get_data_size
import random
from nodes_external_management import hash_pattern
import matplotlib.pyplot as plt
import time
import numpy as np

def init_heur():
    
    global count
    global random_numbers

    random.seed(0)
    random_numbers = [random.random() for i in range(long(1e7))]
    count = 0





""" GAMMA METHOD """




def genpatterns_singlevalues(depth,master_prob,C_set): #generate a pool of patterns using individual dual values
    
    patterns_to_be_added, red_costs = [], []
    
    num_leafs = 2**depth
    
    for l in range(num_leafs):
        
        F = get_Fvector_singlevalues(depth,master_prob,C_set,l)
                        
        p=pattern(l,F,0,[],0)
        
        p.add_missing_rows(depth,C_set)
        
        p.pred_target() #compute target
                
        patterns_to_be_added.append(p)
        
        red_costs.append(compute_rc(depth,p,master_prob))
        
    print('Max red cost in the pool',max(red_costs))
    """
    plt.figure(2)
    from BaP_Node import count_iter
    plt.scatter(count_iter,max(red_costs),color='k')
    plt.pause(0.0001)
    """   
    return patterns_to_be_added, max(red_costs)<0.01

def get_Fvector_singlevalues(depth,master_prob,C_set,leaf):
    
    num_leafs = 2**depth
    num_nodes = num_leafs - 1
    num_features = get_num_features()
    last_index = len(C_set[0][num_features-1]) - 1
    
    parents = get_leaf_parents(leaf, num_nodes)
    F=[0 for h in range(depth)]
    
    for h in range(depth):
        
        j = parents[h]
        
        duals = master_prob.solution.get_dual_values("constraint_3_"+str(leaf)+"_"+str(j)+"_0_0",
                                                     "constraint_3_"+str(leaf)+"_"+str(j)+"_"+str(num_features-1)+"_"+str(last_index))
        
        start = master_prob.linear_constraints.get_indices("constraint_3_"+str(leaf)+"_"+str(j)+"_0_0")
        idx = start + duals.index(min(duals))
                                
        var_name = master_prob.linear_constraints.get_names(int(idx))
                
        tmp=var_name.split("_")
        
        (i,v) = (int(tmp[-2]),int(tmp[-1]))
                            
        F[-1-h]= (i,v)
        
    return F






""" RANDOM PATTERNS """





def genpatterns_random(depth,master_prob,C_set,interesting_leaves):
    
    global count
    global sorted_patterns
    global sorted_H
    global red_costs
    
    nbr_it = 500
    
    theta = np.array([master_prob.solution.get_dual_values("row_constraint_"+str(r)) for r in range(get_data_size())])
    
    patterns_to_be_added, red_costs, H = [0 for it in range(nbr_it)], [-1000 for it in range(nbr_it)], [0 for it in range(nbr_it)]
        
    for it in range(nbr_it):
        
        rdn, count = random_numbers[count], count + 1
        
        l = interesting_leaves[int(rdn*len(interesting_leaves))]
                
        F = gen_Fvector_random(depth,C_set,l)
                        
        p=pattern(l,F,0,[],0)
                                        
        p.add_missing_rows(depth,C_set)
                                        
        p.pred_target() #compute target
        
        ha = hash_pattern(p)
        
        if ha not in H:
            
            H[it] = ha
            
            patterns_to_be_added[it] = p
            
            red_cost = compute_rc(depth,p,master_prob,theta)
            
            red_costs[it] = red_cost
            
    sorted_patterns = [x for _,x in sorted(zip(red_costs,patterns_to_be_added),reverse=True)]
    sorted_H = [x for _,x in sorted(zip(red_costs,H),reverse=True)]
    red_costs.sort(reverse=True)
    
    print('Max red cost in the pool',max(red_costs))
    
    #red_costs.sort(reverse=True)
    
    #for i in range(50):
        
        #print(red_costs[i])
    """    
    plt.figure(2)
    from BaP_Node import count_iter
    plt.scatter(count_iter,max(red_costs),color='k')
    plt.pause(0.0001)
    """                  
    return [sorted_patterns[x] for x in range(100) if red_costs[x]>0.001], max(red_costs) < 0.01

def update_pool(depth,master_prob,C_set,interesting_leaves):
    
    global count
    global sorted_patterns
    global sorted_H
    global red_costs
    
    nbr_it = 200
    
    lenpool=len(sorted_patterns)
    
    patterns_to_be_added, red_costs, H = sorted_patterns[nbr_it/2:lenpool - nbr_it/2], red_costs[nbr_it/2:lenpool - nbr_it/2], sorted_H[nbr_it/2:lenpool - nbr_it/2]
        
    for it in range(nbr_it):
        
        rdn, count = random_numbers[count], count + 1
        
        l = interesting_leaves[int(rdn*len(interesting_leaves))]
        
        F = gen_Fvector_random(depth,C_set,l)
        
        p=pattern(l,F,0,[],0)
                        
        p.add_missing_rows(depth,C_set)
                        
        p.pred_target() #compute target
        
        ha = hash_pattern(p)
        
        if ha not in H:
            
            H.append(ha)
            
            patterns_to_be_added.append(p)
            
            red_costs.append(0)
                
    theta = np.array([master_prob.solution.get_dual_values("row_constraint_"+str(r)) for r in range(get_data_size())])
            
    for p in range(len(patterns_to_be_added)):
        
        if patterns_to_be_added[p]==0:
            
            red_costs[p]=-1000
            
        else:
        
            red_costs[p] = compute_rc(depth,patterns_to_be_added[p],master_prob,theta)
                                    
    sorted_patterns = [x for _,x in sorted(zip(red_costs,patterns_to_be_added),reverse=True)]
    sorted_H = [x for _,x in sorted(zip(red_costs,H),reverse=True)]
    red_costs.sort(reverse=True)
    
    print('Max red cost in the pool',max(red_costs))
    
    #red_costs.sort(reverse=True)
    
    #for i in range(50):
        
        #print(red_costs[i])
    """    
    plt.figure(2)
    from BaP_Node import count_iter
    plt.scatter(count_iter,max(red_costs),color='k')
    plt.pause(0.0001)
    """              

    return [sorted_patterns[p] for p in range(int(nbr_it/2)) if p<len(sorted_patterns) and red_costs[p]>0.001], max(red_costs) < 0.01

def gen_Fvector_random(depth,C_set,l):
    
    global count
    
    F = [0 for h in range(depth)]
    
    parent=get_leaf_parents(l,2**depth-1)
    
    for h in range(depth):
        
        j = parent[-1-h]
        
        non_empty_features = [i for i in range(len(C_set[j])) if len(C_set[j][i])>0]
        
        rdn, count = random_numbers[count], count + 1
        
        i = non_empty_features[int(rdn*len(non_empty_features))]
        
        rdn, count = random_numbers[count], count + 1
        
        v = int(rdn*len(C_set[j][i]))
        
        F[h] = (i,v)
        
    return F



""" RANDOM TREES """



def genpatterns_random_trees(depth,master_prob,C_set):

    global count
    global sorted_patterns
    global sorted_H
    global red_costs
    
    nbr_it = 500 #nbr of trees in the pool
    
    theta = np.array([master_prob.solution.get_dual_values("row_constraint_"+str(r)) for r in range(get_data_size())])
    
    trees, red_costs = [0 for it in range(nbr_it)], [-1000 for it in range(nbr_it)]
        
    for it in range(nbr_it):
        
        F_tree = gen_tree_random(depth,C_set)
        
        tree, red_cost = [], 0
        
        for l in range(len(F_tree)):
            
            F=F_tree[l]
                                        
            p=pattern(l,F,0,[],0)
        
            p.add_missing_rows(depth,C_set)
        
            p.pred_target() #compute target
            
            tree.append(p)
            
            red_cost += compute_rc(depth,p,master_prob,theta)
                                        
        trees[it] = tree
                        
        red_costs[it] = red_cost
            
    sorted_trees = [x for _,x in sorted(zip(red_costs,trees),reverse=True)]
    red_costs.sort(reverse=True)
    
    print('Max red cost in the pool',max(red_costs))
    
    #red_costs.sort(reverse=True)
    
    #for i in range(50):
        
        #print(red_costs[i])
    """    
    plt.figure(2)
    from BaP_Node import count_iter
    plt.scatter(count_iter,max(red_costs),color='k')
    plt.pause(0.0001)
    """                  
    return [sorted_trees[tr][pat] for tr in range(20) for pat in range(2**depth) if red_costs[tr]>0.001], max(red_costs) < -4


def gen_tree_random(depth,C_set):
    
    global count
    
    num_features = get_num_features()
    
    num_leafs = 2**depth
    
    num_nodes = 2**depth - 1
    
    thr = []
    
    for j in range(num_nodes):
        
        rdn, count = random_numbers[count], count + 1
        
        i = int(rdn*num_features)
        
        rdn, count = random_numbers[count], count + 1
        
        v = int(rdn*len(C_set[j][i]))
        
        thr.append((i,v))

    T=[]
    
    for l in range(num_leafs):
        
        parents=get_leaf_parents(l,num_nodes)
        
        F=[]
        
        for h in range(depth):
            
            j = parents[-h-1]
            
            F.append(thr[j])

        T.append(F)
        
    return T


def compute_rc(depth,p,master_prob,theta):
    
    l=p.leaf
    
    rc = p.c - master_prob.solution.get_dual_values("constraint_2_" + str(l))
        
    parents = get_leaf_parents(l,2**depth - 1)
    
    for h in range(depth):
        
        (i,v), j = p.F[h], parents[-h-1]
    
        rc -= master_prob.solution.get_dual_values("constraint_3_"+str(l)+"_"+str(j)+"_"+str(i)+"_"+str(v))
                
    rc -= np.sum(theta[p.R])
        
    return rc