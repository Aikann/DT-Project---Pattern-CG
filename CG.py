# -*- coding: utf-8 -*- 
"""
Created on Tue Apr 10 13:44:53 2018

@author: Guillaume
"""

from RMPSolver import add_column, solveRMP
from utility import give_solution_type, hash_pattern
from PricingSolver import solve_pricing, avoid_method, init_pricing_probs
from learn_tree_funcs import get_leaf_parents, get_data_size, get_num_targets
import time
from heuristics import genpatterns_random, update_pool


def obtain_depth(d):
    """ Obtain the global parameter depth
    
    Input:
        d (integer): maximum depth
        
    Output:
        none
    """
    
    global depth
    depth=d


class BaP_Node:
    
    def __init__(self,patterns_set,prob,ID,parent,H,branch_var,branch_index,master_thresholds):
        """ Construct a node in the branch and price tree. Eventually there is not any BaP in our algorithm, but the structure 
        can still be used.
    
        Input:
            patterns_set (list of list of patterns): patterns available for the master problem
            prob (Cplex problem): master problem at this node
            ID (string): ID of the node
            parent (BaP_Node): parent node in the BaP tree
            H (list of list of floats): hash table corresponding to the patterns
            branch_var (unused)
            branch_index (unused)
            master_thresholds (list of triples): set of index corresponding to C_set
            
        Output:
            self (BaP_Node)
        """
        
        self.prob=prob #cplex problem
        self.patterns_set=patterns_set #list containing lists of sets for each leaf
        self.ID = ID
        self.parent = parent
        self.H = H #hash table for patterns
        self.branch_var = branch_var #type of branched variables
        self.branch_index = branch_index #index of the variables
        self.master_thresholds = master_thresholds #set of triples
        
    def explore(self,C_set,timelimit): #do CG until the master problem is solved
        """ Run CG until optimaity has been proven or time limit has been reached
    
        Input:
            C_set (list of list of list of floats): restricted thresholds set
            timelimit (integer): time limit in seconds
            
        Output:
            none (works in place such that all the information is contained in self)       
        """
        
        start=time.time()
                                
        convergence = False
        
        first_time = True
        
        avoid_method(depth)
                                
        solveRMP(self.prob)
        
        global count_iter
        
        count_iter=1
                                
        red_cost = float('+inf')
        
        go_pricing, bad_pool, loop = 0, False, 0
        
        interesting_leaves = [l for l in range(2**depth)]
        
        while not convergence and loop<10:
            
            c=time.time()
                                                
            solveRMP(self.prob)
                        
            t=time.time()-c
                                    
            print(count_iter,"Time MP :",t)
                                                        
            if (go_pricing>1 or red_cost<0.001) and ((not first_time) or (time.time()-start<8.5*60)):# or count_iter%15==0 or(count_iter>500 and count_iter%5==0):
                
                if first_time:
                    
                    print('Constructing problems...')
                
                    init_pricing_probs(depth,C_set)
                    
                    first_time = False
                        
                b=time.time()
                                    
                patterns_to_be_added, convergence, red_cost, interesting_leaves = solve_pricing(depth,
                self.prob,self.master_thresholds,C_set)
            
                print(count_iter,"Time pricing :",time.time()-b)
                
                go_pricing, bad_pool = 0, True
                
            else:
                
                a=time.time()
                
                if count_iter==1 or bad_pool:
                
                    patterns_to_be_added, bad_pool = genpatterns_random(depth,self.prob,C_set,interesting_leaves)
                                            
                    go_pricing+=1
                    
                    if get_data_size()>10000 or (get_num_targets()>8 and get_data_size()>2000):
                        
                        go_pricing=0
                        loop+=1
                    
                else:
                    
                    patterns_to_be_added, bad_pool = update_pool(depth,self.prob,C_set,interesting_leaves)
                    
                    go_pricing=0
                    loop=0
            
            print('Pool generation time: '+str(time.time()-a))
            
            if count_iter%10==0:
            
                print("Current solution value "+str(self.prob.solution.get_objective_value()))
            
                print("Number of patterns "+str(sum([len(self.patterns_set[l]) for l in range(len(self.patterns_set))])))
                
            if time.time()-start>timelimit:
                    
                self.solution_value = self.prob.solution.get_objective_value()
                self.solution = self.prob.solution.get_values()
                self.solution_type = give_solution_type(self.prob)
                
                return
                                                                                   
            if not convergence and loop<10:
                
                a=time.time()
                                                                
                self.add_patterns(patterns_to_be_added,True)
                
                print('Time add columns: '+str(time.time()-a))
                                                                                
            count_iter=count_iter+1
        
        self.solution_value = self.prob.solution.get_objective_value()
        self.solution = self.prob.solution.get_values()
        self.solution_type = give_solution_type(self.prob)
        
    def add_patterns(self,patterns_to_add,safe_insertion=False):
        """ Add patterns to the master
    
        Input:
            patterns_to_add (list of patterns): patterns to be added in the master
            safe_insertion (bool): if true, this function checks that the pattern does not already exist thanks to a hash table
            
        Output:
            none (works in place)
        """
        
        num_nodes = len(self.patterns_set) - 1
                        
        for p in patterns_to_add:
            
            l = p.leaf
                            
            if safe_insertion:
                
                hp = hash_pattern(p)
                                                                                                                
                if hp not in self.H[l]:
                
                    self.patterns_set[l].append(p)
                                            
                    self.H[l].append(hp)
                    
                    parents = get_leaf_parents(l,num_nodes)
                    
                    for h in range(depth):
                        
                        j = parents[-h-1]
                        
                        (i,v) = p.F[h]
                        
                        if (j,i,v) not in self.master_thresholds:
                            
                            self.master_thresholds.append((j,i,v))
                          
                    self.prob = add_column(depth,self.prob,self.patterns_set[l],p)
                    
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
                