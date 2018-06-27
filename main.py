# -*- coding: utf-8 -*-
"""
Created on Tue Apr 10 13:09:31 2018

@author: Guillaume
"""

from BBSolver import BBSolver
import getopt
import sys
from Instance import create_instance, create_first_solution, initialize_global_values, empty_patterns, restricted_C_set, restricted_C_set2
from Cmodule import brute_force_solver
import time
from testmodule import test, create_train_and_test
import numpy as np
import xlsxwriter

def main(argv):
        
    try:
       
        opts, args = getopt.getopt(argv,"f:d:p:",["ifile=","depth=","postprocessing="])

    except getopt.GetoptError:
       
        sys.exit(2)
      
    for opt, arg in opts:

        if opt in ("-f", "--ifile"):

            inputfile = arg
        
        elif opt in ("-d", "--depth"):

            inputdepth = int(arg)
            
        elif opt in ("-p", "--postprocessing"):
            
            postp= int(arg)
            
    if False and postp==inputdepth:
        
        print("Solving with brute force algorithm")
        
        brute_force_solver(inputfile,inputdepth)
        
        print("The optimal tree can be found in results_brute_force.txt")
        
        return [], []
        
    else:
        
        print("Solving with CG algorithm")
            
        print('Initializing...')
                
        create_instance(inputfile)
                                                           
        patterns_set, master_thresholds, TARGETS, C_set = create_first_solution(inputdepth)
        
        #C_set, master_thresholds = restricted_C_set(C_set,patterns_set,inputdepth)
        
        C_set, master_thresholds = restricted_C_set2(C_set,patterns_set,inputdepth)
                                
        best_solution_value = sum([patterns_set[l][0].c for l in range(2**inputdepth)])
        
        initialize_global_values(TARGETS,inputdepth)
        
        print('Initialization done')
                        
        return BBSolver(TARGETS, patterns_set, best_solution_value, inputdepth, C_set, master_thresholds,postp), C_set


DIR="D:\Travail\X\Stage 3A\DT Project - Pattern CG\Instances\\"    
#tree, C_set = main(["-f"+DIR+"chess.csv","-d 3","-p 2"])

#score=test(tree,C_set,"IndiansDiabetestest.csv")
        

def run_tests(instances,depths,postprocessing):
        
    sol=[]
    val=[]
    r_time=[]
    workbook = xlsxwriter.Workbook('RUN.xlsx')
    worksheet = workbook.add_worksheet()
    worksheet.write(0,1,"Instance")
    worksheet.write(0,2,"Mean")
    worksheet.write(0,3,"Worst")
    worksheet.write(0,4,"Time")
    
    for inst in range(len(instances)):
        
        for k in depths:
            
            for p in postprocessing:
                
                sol=[]
                val=[]
                r_time=[]
                    
                trainfiles, testfiles = create_train_and_test(instances[inst]+".csv",5,DIR)
                
                for nbr_test in range(len(testfiles)):
                                                
                        trainfile=trainfiles[nbr_test]
                        testfile=testfiles[nbr_test]
                
                        a=time.time()
                        
                        tree, C_set = main(["-f"+trainfile,"-d "+str(k),"-p "+str(p)])
                        
                        real_time = time.time() - a
                        
                        score=test(tree,C_set,testfile)
                        
                        sol.append((instances[inst].split("\\")[-1],k,nbr_test,score,p,real_time))
                        
                        val.append(score)
                        
                        r_time.append(real_time)
                        
                write_in_excel(worksheet,inst,instances[inst].split("\\")[-1],val,r_time)
        
    workbook.close()
            
    return sol, val, r_time

def write_in_excel(worksheet,count,name,val,r_time):
        
    worksheet.write(count+1,1,name)
    worksheet.write(count+1,2,str(100*round(np.mean(val),3)))
    worksheet.write(count+1,3,str(100*round(np.min(val),3)))
    worksheet.write(count+1,4,str(round(np.mean(r_time),2)))
    
    
    
ALL_INSTANCES=["iris","IndiansDiabetes","banknote","balance-scale","monk1","monk2","monk3","Ionosphere","spambase","car_evaluation","biodeg"
               ,"seismic_bumps","Statlog_satellite","tic-tac-toe","wine"]
instances=[DIR+i for i in ALL_INSTANCES[8:15]]#"IndiansDiabetes","bank_conv","messidor"]#,"magic04"]
postprocessing=[2]
depths = [3]
timelimit=10*60
sol,val, r_time=run_tests(instances,depths,postprocessing)
print(np.mean(val),np.min(val-np.mean(val)),np.mean(r_time)/60.0)