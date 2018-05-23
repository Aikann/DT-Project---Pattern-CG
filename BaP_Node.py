# -*- coding: utf-8 -*-
"""
Created on Tue Apr 10 13:44:53 2018

@author: Guillaume
"""

from RMPSolver import add_column, solveRMP, create_new_master, display_prob_lite
from nodes_external_management import give_solution_type, hash_pattern
from PricingSolver import solve_pricing
from learn_tree_funcs import get_leaf_parents
import time
import matplotlib.pyplot as plt
from copy import deepcopy as dc


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
        
        plt.figure()
                
        plt.show()
                        
        #print(self.segments_set)
                
        convergence = False
                
        solveRMP(self.prob)
                                                                
        if give_solution_type(self.prob) == 'infeasible':
                        
            self.solution_type = 'infeasible'
            self.solution_value = float('+inf')
            
            return
        
        global count_iter
        
        count_iter=1
                                
        red_cost = float('-inf')
        
        while not convergence:
            
            c=time.time()
                                    
            solveRMP(self.prob)
                                    
            print(count_iter,"Time MP :",time.time()-c)
                                                
            pricing_method = 1
                        
            b=time.time()
                                    
            patterns_to_be_added, convergence, red_cost = solve_pricing(depth,
            self.prob,self.patterns_set,self.branch_var,
            self.branch_index,self.ID,self.master_thresholds,C_set,pricing_method)
            
            print(count_iter,"Time pricing :",time.time()-b)
            
            plt.scatter(count_iter,self.prob.solution.get_objective_value(),color='g')
            
            plt.pause(0.01)
            
            if float(self.prob.solution.get_objective_value()) >= UB: #check if it is useful to continue
                
                self.solution_value = self.prob.solution.get_objective_value()
                self.solution = self.prob.solution.get_values()
                self.solution_type = give_solution_type(self.prob)
                
                return
            
            if count_iter%100==0:
            
                print("Current solution value "+str(self.prob.solution.get_objective_value()))
            
                print("Number of patterns "+str(sum([len(self.patterns_set[l]) for l in range(len(self.patterns_set))])))
                
                #check_unicity(self.segments_set)
                        
                for p in self.patterns_set[0]:
                                               
                    print(p)
                
                #print(patterns_to_be_added)
                
                #print("Master thresholds",self.master_thresholds)
                
                #display_prob_lite(self.prob,"dual")
                
                #display_prob_lite(self.prob,"primal")
                
                #print(self.prob.solution.get_reduced_costs())
                
                #for i in self.prob.variables.get_names():
                
                    #print(i,self.prob.solution.get_reduced_costs(i))
                
                #display_RMP_solution_dual(depth,self.prob,count_iter)
                
                #display_RMP_solution_primal(depth,self.prob,count_iter,self.segments_set)
                
                #print(self.prob.variables.get_num())
                
                input()
                                                
            a=time.time()
                        
            #print("Full set",self.segments_set)
                                    
            #print("Full set after addition",self.segments_set)
                        
            if not convergence:
                                                
                self.add_patterns(patterns_to_be_added,True)
                                                                    
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
                        
    def create_children_by_branching(self,var,index): #TODO;
        
        return
                