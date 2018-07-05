# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 10:12:37 2018

@author: Guillaume
"""

from RMPSolver import create_new_master, display_prob_lite
from BaP_Node import BaP_Node
import time
from nodes_external_management import hash_pattern
from learn_tree_funcs import get_depth, get_leaf_parents
import matplotlib.pyplot as plt
from Instance import post_files
import numpy as np
from Cmodule import execute_C_code, write_C_subp, get_res, get_new_thresholds
import copy

chosen_method = "HORIZONTAL_SEARCH"

def BBSolver(TARGETS,patterns_set,best_solution_value,inputdepth,C_set,master_thresholds,postp,algo):
    
    prob=create_new_master(inputdepth,patterns_set,master_thresholds,C_set)
    
    H = [[0] for l in range(len(patterns_set))]
    
    for l in range(len(patterns_set)):
        
        for p in range(len(patterns_set[l])):
        
            H[l].append(hash_pattern(patterns_set[l][p]))
                            
    root_node=BaP_Node(patterns_set,prob,"",None,H,[],[],master_thresholds) #construct root node
    
    if postp>=1:
        
        for i in root_node.prob.variables.get_names():
    
            root_node.prob.variables.set_types(i,"B")
        
        root_node.prob.solve()
        
        best_solution_value = root_node.prob.solution.get_objective_value()
        
        root_node.CORR = []
    
        for l in range(2**(inputdepth-postp)):
            
            step=2*postp
                                
            p1 = next(root_node.patterns_set[step*l][pat] for pat in range(len(root_node.patterns_set[step*l])) if float(root_node.prob.solution.get_values("pattern_"+str(pat)+"_"+str(step*l)))>=0.99)
        
            p2 = next(root_node.patterns_set[step*l+1][pat2] for pat2 in range(len(root_node.patterns_set[step*l +1])) if float(root_node.prob.solution.get_values("pattern_"+str(pat2)+"_"+str(step*l+1)))>=0.99)
            
            if postp==2:
            
                p3 = next(root_node.patterns_set[step*l+2][pat3] for pat3 in range(len(root_node.patterns_set[step*l +2])) if float(root_node.prob.solution.get_values("pattern_"+str(pat3)+"_"+str(step*l+2)))>=0.99)
    
                p4 = next(root_node.patterns_set[step*l+3][pat4] for pat4 in range(len(root_node.patterns_set[step*l +3])) if float(root_node.prob.solution.get_values("pattern_"+str(pat4)+"_"+str(step*l+3)))>=0.99)

                rows = p1.R + p2.R + p3.R + p4.R
                
                root_node.CORR.append(p1.c+p2.c+p3.c+p4.c)
                
            else:
                
                rows = p1.R + p2.R
                
                root_node.CORR.append(p1.c+p2.c)
            
            #print("Erreur ID "+str(l)+": "+str(p1.e+p2.e+p3.e+p4.e))
            
            #print("Good predictions ID "+str(l)+": "+str(p1.c+p2.c+p3.c+p4.c))
            
            post_files(rows,l)
                 
        root_node.CORR = np.array(root_node.CORR)
        
        print("Best solution: "+str(best_solution_value))
                        
        final_tree=[]
        
        new_thresholds=[]
                    
        print("Starting post-processing...")
        
        b=time.time()
        
        progress=[]
                
        for l in range(2**(inputdepth-postp)):
            
            print(l)
            
            write_C_subp(l,postp)
            
            execute_C_code(l)
            
            res=get_res(l)
            
            progress.append(res-root_node.CORR[l])
                        
            new_thresholds.extend(get_new_thresholds(l,postp))
                            
        for (j,i,thr) in new_thresholds:
            
            if thr not in C_set[j][i]:
                
                C_set[j][i].append(thr)
                
                master_thresholds.append((j,i,len(C_set[j][i])-1))
                                        
        for leaf in range(2**inputdepth):
            
            p = next(root_node.patterns_set[leaf][pat] for pat in range(len(root_node.patterns_set[leaf])) if float(root_node.prob.solution.get_values("pattern_"+str(pat)+"_"+str(leaf)))>=0.99)
    
            p2 = copy.deepcopy(p)
            
            p2.R=[]
            
            for (j,i,thr) in new_thresholds:
                
                if j in get_leaf_parents(leaf,2**inputdepth - 1):
                    
                    h = get_depth(j,2**inputdepth - 1) - 1
                
                    p2.F[h]=(i,C_set[j][i].index(thr))
                    
            p2.add_missing_rows(inputdepth,C_set)
            
            p2.pred_target()
                                            
            final_tree.append(p2)
                                
        total_progress = sum(progress)
        
        print("Post-processing time: "+str(time.time()-b))
        
        best_solution_value = best_solution_value+total_progress
        
        print('Final score after post-processing: '+str(best_solution_value))
        
        print(best_solution_value,sum( [final_tree[i].c for i in range(len(final_tree))] ),total_progress)
                            
        assert(sum( [final_tree[i].c for i in range(len(final_tree))] ) == best_solution_value)
        
    if algo=='CART*':
                
        return final_tree
    
    #write_tree(inputdepth,root_node,C_set)
    """ PART 2 """
    """
    """
    """
    """
    
    if postp >=1:
    
        patterns_set=[[final_tree[i]] for i in range(len(final_tree))]
        
        prob=create_new_master(inputdepth,patterns_set,master_thresholds,C_set)
        
        H = [[0] for l in range(len(patterns_set))]
        
        for l in range(len(patterns_set)):
            
            for p in range(len(patterns_set[l])):
            
                H[l].append(hash_pattern(patterns_set[l][p]))
                            
        root_node=BaP_Node(patterns_set,prob,"",None,H,[],[],master_thresholds) #construct root node
            
    a=time.time()
    
    root_node.explore(30000,C_set)
    
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
    
    root_node.CORR = []
    
    if postp>=1:
    
        for l in range(2**(inputdepth-postp)):
            
            step=2*postp
                                
            p1 = next(root_node.patterns_set[step*l][pat] for pat in range(len(root_node.patterns_set[step*l])) if float(root_node.prob.solution.get_values("pattern_"+str(pat)+"_"+str(step*l)))>=0.99)
        
            p2 = next(root_node.patterns_set[step*l+1][pat2] for pat2 in range(len(root_node.patterns_set[step*l +1])) if float(root_node.prob.solution.get_values("pattern_"+str(pat2)+"_"+str(step*l+1)))>=0.99)
            
            if postp==2:
            
                p3 = next(root_node.patterns_set[step*l+2][pat3] for pat3 in range(len(root_node.patterns_set[step*l +2])) if float(root_node.prob.solution.get_values("pattern_"+str(pat3)+"_"+str(step*l+2)))>=0.99)
    
                p4 = next(root_node.patterns_set[step*l+3][pat4] for pat4 in range(len(root_node.patterns_set[step*l +3])) if float(root_node.prob.solution.get_values("pattern_"+str(pat4)+"_"+str(step*l+3)))>=0.99)

                rows = p1.R + p2.R + p3.R + p4.R
                
                root_node.CORR.append(p1.c+p2.c+p3.c+p4.c)
                
            else:
                
                rows = p1.R + p2.R
                
                root_node.CORR.append(p1.c+p2.c)
            
            #print("Erreur ID "+str(l)+": "+str(p1.e+p2.e+p3.e+p4.e))
            
            #print("Good predictions ID "+str(l)+": "+str(p1.c+p2.c+p3.c+p4.c))
            
            post_files(rows,l)
                 
    root_node.CORR = np.array(root_node.CORR)
        
    print("Best solution: "+str(best_solution_value))
                
    if postp>=1:
        
        final_tree=[]
        
        new_thresholds=[]
                    
        print("Starting post-processing...")
        
        b=time.time()
        
        progress=[]
                
        for l in range(2**(inputdepth-postp)):
            
            print(l)
            
            write_C_subp(l,postp)
            
            execute_C_code(l)
            
            res=get_res(l)
            
            progress.append(res-root_node.CORR[l])
            
            if postp==2:
            
                new_thresholds.extend(get_new_thresholds(l,postp))
                
                print(new_thresholds)
                
        for (j,i,thr) in new_thresholds:
            
            if thr not in C_set[j][i]:
                
                C_set[j][i].append(thr)
                                        
        for leaf in range(2**inputdepth):
            
            p = next(root_node.patterns_set[leaf][pat] for pat in range(len(root_node.patterns_set[leaf])) if float(root_node.prob.solution.get_values("pattern_"+str(pat)+"_"+str(leaf)))>=0.99)
    
            p2 = copy.deepcopy(p)
            
            p2.R=[]
            
            for (j,i,thr) in new_thresholds:
                
                if j in get_leaf_parents(leaf,2**inputdepth - 1):
                    
                    h = get_depth(j,2**inputdepth - 1) - 1
                
                    p2.F[h]=(i,C_set[j][i].index(thr))
                    
            p2.add_missing_rows(inputdepth,C_set)
            
            p2.pred_target()
                                            
            final_tree.append(p2)
                                
        total_progress = sum(progress)
        
        print("Post-processing time: "+str(time.time()-b))
        
        best_solution_value = best_solution_value+total_progress
        
        print('Final score after post-processing: '+str(best_solution_value))
        
        print(sum( [final_tree[i].c for i in range(len(final_tree))] ), best_solution_value)
        
        if sum( [final_tree[i].c for i in range(len(final_tree))] ) != int(best_solution_value):
            
            print()
                            
        #assert(sum( [final_tree[i].c for i in range(len(final_tree))] ) == best_solution_value)
    
    print("Total time :"+str(time.time() - a))
    
    if postp>=1:
    
        return final_tree
    
    else:
        
        final_tree=[]
        
        for leaf in range(2**inputdepth):
            
            final_tree.append(next(root_node.patterns_set[leaf][pat] for pat in range(len(root_node.patterns_set[leaf])) if float(root_node.prob.solution.get_values("pattern_"+str(pat)+"_"+str(leaf)))>=0.99))
    
        return final_tree
    
    
def write_tree(depth,root_node,C_set):
    
    num_nodes = 2**depth - 1
    
    f=open("results_CG.txt","w")
    
    for h in range(depth-2):
        
        cnt=0
        
        for j in range(num_nodes):
            
            if int(get_depth(j,num_nodes)-1)==h:
                
                ID = 2**h - 1 + cnt
                
                cnt += 1
                
                var = next(v for v in root_node.prob.variables.get_names() if ("rho_"+str(j) in v) and float(root_node.prob.solution.get_values(v))>=0.99)
                
                tmp=var.split("_")
        
                (i,v) = (int(tmp[-2]),int(tmp[-1]))
                
                threshold = C_set[j][i][v]
                
                f.write("Nd"+str(ID)+" : Feat_"+str(i)+", threshold "+str(threshold)+"\n")
                
    for t in range(2**(depth-2)):
        
        f.write("\n")
        
        f.write("subtree_"+str(t)+"\n")
        
        fr = open("results_subp_"+str(t)+".txt","r")
        
        for line in fr.readlines():
            
            f.write(line)
            
        fr.close()
        
    f.close()
    
    print("The optimal tree can be found in results_CG.txt")
    
    
                
                
                