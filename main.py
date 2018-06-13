# -*- coding: utf-8 -*-
"""
Created on Tue Apr 10 13:09:31 2018

@author: Guillaume
"""

from BBSolver import BBSolver
import getopt
import sys
from Instance import create_instance, create_first_solution, initialize_global_values, empty_patterns, restricted_C_set, restricted_C_set2
from pattern import create_FT

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
            
    print('Initializing...')
            
    create_instance(inputfile)
                                               
    patterns_set, master_thresholds, TARGETS, C_set = create_first_solution(inputdepth)
    
    #C_set, master_thresholds = restricted_C_set(C_set,patterns_set,inputdepth)
    
    C_set, master_thresholds = restricted_C_set2(C_set,patterns_set,inputdepth)
        
    #create_FT(C_set)
                
    best_solution_value = sum([patterns_set[l][0].c for l in range(2**inputdepth)])
    
    initialize_global_values(TARGETS,inputdepth)
    
    print('Initialization done')
                        
    return BBSolver(TARGETS, patterns_set, best_solution_value, inputdepth, C_set, master_thresholds)
    
root=main(["-fIndiansDiabetes.csv","-d 5"])