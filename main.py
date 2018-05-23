# -*- coding: utf-8 -*-
"""
Created on Tue Apr 10 13:09:31 2018

@author: Guillaume
"""

from BBSolver import BBSolver
import getopt
import sys
from Instance import create_instance, create_first_solution, initialize_global_values, basic_patterns, compute_C_set

def main(argv):
        
    try:
       
        opts, args = getopt.getopt(argv,"f:d:",["ifile=","depth="])

    except getopt.GetoptError:
       
        sys.exit(2)
      
    for opt, arg in opts:

        if opt in ("-f", "--ifile"):

            inputfile = arg
        
        elif opt in ("-d", "--depth"):

            inputdepth = int(arg)
            
    create_instance(inputfile)
                   
    TARGETS = create_first_solution(inputdepth) #only return targets for the time being
    
    C_set = compute_C_set()
            
    patterns_set, master_thresholds = basic_patterns(inputdepth,C_set)
                
    best_solution_value = 0
    
    for l in range(len(patterns_set)):
        
        for p in patterns_set[l]:
            
            print(p)
            
    initialize_global_values(TARGETS,inputdepth,C_set)
                        
    return BBSolver(TARGETS, patterns_set, best_solution_value, inputdepth, C_set, master_thresholds)
    
root=main(["-fIndiansDiabetes.csv","-d 1"])