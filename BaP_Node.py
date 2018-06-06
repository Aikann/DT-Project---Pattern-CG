# -*- coding: utf-8 -*-
"""
Created on Tue Apr 10 13:44:53 2018

@author: Guillaume
"""

from RMPSolver import add_column, solveRMP, create_new_master, display_prob_lite
from nodes_external_management import give_solution_type, hash_pattern
from PricingSolver import solve_pricing, avoid_method, init_pricing_probs
from learn_tree_funcs import get_leaf_parents
import time
import matplotlib.pyplot as plt
from heuristics import genpatterns_singlevalues, genpatterns_random, update_pool, genpatterns_random_trees
import numpy as np


def obtain_depth(d):
    
    global depth
    depth=d


class BaP_Node:
    
    def __init__(self,patterns_set,prob,ID,parent,H,branch_var,branch_index,master_thresholds):
        
        self.prob=prob #cplex problem
        self.patterns_set=patterns_set #list containing lists of sets for each leaf
        self.ID = ID
        self.parent = parent
        self.H = H #hash table for patterns
        self.branch_var = branch_var #type of branched variables
        self.branch_index = branch_index #index of the variables
        self.master_thresholds = master_thresholds #set of triples
        
    def explore(self,UB,C_set): #do CG until the master problem is solved
        
        init_pricing_probs(depth,C_set)
        """
        plt.figure(1)
        
        plt.ylim(ymax=800)
        
        plt.title("Master objective value")
        
        plt.figure(2)
        
        plt.title("Reduced costs")
        
        plt.figure(3)
        
        plt.title("Time to solve master")
               
        plt.show()
        """                               
        convergence = False
        
        #○avoid_method(depth)
        
        #self.prob.write('here.lp','lp')
                        
        solveRMP(self.prob)
                                                                        
        if give_solution_type(self.prob) == 'infeasible':
                        
            self.solution_type = 'infeasible'
            self.solution_value = float('+inf')
            
            return
        
        global count_iter
        
        count_iter=1
                                
        red_cost = float('+inf')
        
        go_pricing, bad_pool = False, False
        
        interesting_leaves = [l for l in range(2**depth)]
        
        while not convergence:
            
            c=time.time()
                                                
            solveRMP(self.prob)
                        
            t=time.time()-c
                                    
            print(count_iter,"Time MP :",t)
            
            #print("RC of initial solution: "+str(sum([self.prob.solution.get_reduced_costs("pattern_0_"+str(l)) for l in range(2**depth)])))
            """
            plt.figure(3)
            
            plt.scatter(count_iter,t,color='r')
            
            plt.pause(0.0001)
            """                                   
            pricing_method = 1
            
            if go_pricing>9 or red_cost<0.001:# or count_iter%15==0 or(count_iter>500 and count_iter%5==0):
                        
                b=time.time()
                                    
                patterns_to_be_added, convergence, red_cost, interesting_leaves = solve_pricing(depth,
                self.prob,self.patterns_set,self.branch_var,
                self.branch_index,self.ID,self.master_thresholds,C_set,pricing_method)
            
                print(count_iter,"Time pricing :",time.time()-b)
                
                go_pricing, bad_pool = 0, True
                
            else:
                
                a=time.time()
                
                if count_iter<0:
                
                    patterns_to_be_added, go_pricing = genpatterns_random_trees(depth,self.prob,C_set)
                    
                else:
                
                    if count_iter==1 or bad_pool:
                    
                        patterns_to_be_added, bad_pool = genpatterns_random(depth,self.prob,C_set,interesting_leaves)
                                                
                        go_pricing+=1
                        
                    else:
                        
                        patterns_to_be_added, bad_pool = update_pool(depth,self.prob,C_set,interesting_leaves)
                        
                        go_pricing=0
                
                print('Pool generation time: '+str(time.time()-a))
                
                #input()
            """    
            plt.figure(1)
            
            plt.ylim(ymax=800)
                
            plt.scatter(count_iter,self.prob.solution.get_objective_value(),color='g')
            
            plt.pause(0.0001)
            """
            if float(self.prob.solution.get_objective_value()) >= UB: #check if it is useful to continue
                
                self.solution_value = self.prob.solution.get_objective_value()
                self.solution = self.prob.solution.get_values()
                self.solution_type = give_solution_type(self.prob)
                
                return
            
            if count_iter%10==0:
            
                print("Current solution value "+str(self.prob.solution.get_objective_value()))
            
                print("Number of patterns "+str(sum([len(self.patterns_set[l]) for l in range(len(self.patterns_set))])))
                
                #check_unicity(self.segments_set)
                        
                #for p in self.patterns_set[0]:
                                               
                    #print(p)
                    
                #print(patterns_to_be_added[0])
                
                #print("Master thresholds",self.master_thresholds)
                
                #display_prob_lite(self.prob,"dual")
                
                #print(self.prob.solution.get_reduced_costs())
                
                #for i in self.prob.variables.get_names():
                
                    #print(i,self.prob.solution.get_reduced_costs(i))
                                                
                #print(self.prob.variables.get_num())
                
                #input()
                
            if count_iter%5000==0:
                
                a=input()
                
                if a =="stop":
                    
                    return
                                                
            a=time.time()
                        
            #print("Full set",self.segments_set)
                                    
            #print("Full set after addition",self.segments_set)
            """
            if(sum([len(self.patterns_set[l]) for l in range(2**depth)]) > 7000):
                
                print('Cleaning')
                
                self.clean(C_set)
            """            
            if not convergence:
                
                a=time.time()
                                                                
                self.add_patterns(patterns_to_be_added,True)
                
                print('Time add columns: '+str(time.time()-a))
                                                                    
            print(count_iter,"Time MP construction :",time.time()-a)
            
            
            count_iter=count_iter+1
            
        
        self.solution_value = self.prob.solution.get_objective_value()
        self.solution = self.prob.solution.get_values()
        self.solution_type = give_solution_type(self.prob)
        
    def add_patterns(self,patterns_to_add,safe_insertion=False):
        
        num_nodes = len(self.patterns_set) - 1
                        
        for p in patterns_to_add:
            
            l = p.leaf
                            
            if safe_insertion:
                                                                                                                
                if hash_pattern(p) not in self.H[l]:
                
                    self.patterns_set[l].append(p)
                                            
                    self.H[l].append(hash_pattern(p))
                    
                    for h in range(depth):
                        
                        j = get_leaf_parents(l,num_nodes)[-h-1]
                        
                        (i,v) = p.F[h]
                        
                        if (j,i,v) not in self.master_thresholds:
                            
                            self.master_thresholds.append((j,i,v))
                            
                    self.prob = add_column(depth,self.prob,self.patterns_set[l],p,l,self.master_thresholds)
                    
                else:
                    
                    p = []
                        
            else:
                    
                self.patterns_set[l].append(p)
                                        
                self.H[l].append(hash_pattern(p))
                
                for h in range(depth):
                        
                        j = get_leaf_parents(l,num_nodes)[-h-1]
                        
                        (i,v) = p.F[h]
                        
                        if (j,i,v) not in self.master_thresholds:
                            
                            self.master_thresholds.append((j,i,v))
                        
    def clean(self,C_set):
        
        new_patterns_set = [[] for l in range(len(self.patterns_set))]
        
        names = np.array(self.prob.variables.get_names())
        
        values = np.array(self.prob.solution.get_values())
        
        idx = np.where(values > 0.001)[0]
                
        names, values = names[idx], values[idx]
                
        for n in names:
                        
            if "pattern" in n:
                
                tmp = n.split("_")
                
                l = int(tmp[-1])
                
                p = int(tmp[-2])
                
                new_patterns_set[l].append(self.patterns_set[l][p])
                
        self.patterns_set = new_patterns_set
        
        self.prob = create_new_master(depth,self.patterns_set,self.master_thresholds,C_set)
        
        self.prob.write('here.lp','lp')
        
        return
                