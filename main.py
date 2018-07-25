# -*- coding: utf-8 -*-
""" 
Created on Tue Apr 10 13:09:31 2018

@author: Guillaume
"""

from MainSolver import tree
import getopt
import sys
from Instance import create_instance, create_first_solution, initialize_global_values, restricted_C_set2
import time
from testmodule import test, create_train_and_test
import numpy as np
import xlsxwriter
import os
from regtrees2 import genCART

def main(argv):
    """ Run the algorithm with the given parameters
    
    Input:
        argv (list of strings): parameters of the problem/algorithm
        
    Output:
        tree (list of patterns): the final decision tree
        C_set (list of list of list of floats): restricted thresholds set
    """
        
    try:
       
        opts, args = getopt.getopt(argv,"f:d:p:a:t:",["ifile=","depth=","postprocessing=","algorithm=","timelimit="])

    except getopt.GetoptError:
       
        sys.exit(2)
      
    for opt, arg in opts:

        if opt in ("-f", "--ifile"):

            inputfile = arg
        
        elif opt in ("-d", "--depth"):

            inputdepth = int(arg)
            
        elif opt in ("-p", "--postprocessing"):
            
            postp= int(arg)
            
        elif opt in ("-a","--algorithm"):
            
            algo = arg
            
        elif opt in ("-t","--timelimit"):
            
            timelimit = int(arg)
            
    print('Initializing...')
            
    create_instance(inputfile)
                                                       
    patterns_set, master_thresholds, TARGETS, C_set = create_first_solution(inputdepth)
        
    C_set, master_thresholds = restricted_C_set2(C_set,patterns_set,inputdepth)
                            
    best_solution_value = sum([patterns_set[l][0].c for l in range(2**inputdepth)])
    
    initialize_global_values(TARGETS,inputdepth)
    
    print('Initialization done')
                    
    return tree(TARGETS, patterns_set, best_solution_value, inputdepth, C_set, master_thresholds,timelimit), C_set

        

def run_tests(instances,depths,postprocessing,algo,tl):
    """ Run testing method with CG and write it in a xlsx file
    
    Input:
        instances (list of string): names of the instances
        depths (list of integers): maximum depths to be considered
        postprocessing (integer): postprocessing method, disabled in this version, should be 0
        algo (string): algorithm to use, disabled in this version, should be CG
        tl (integer): time limit in seconds
        
    Output:
        sol (list of multi type): diverse information about the results
    """
        
    sol=[]
    val=[]
    r_time=[]
    workbook = xlsxwriter.Workbook('RUN.xlsx')
    worksheet = workbook.add_worksheet()
    worksheet.write(0,1,"Instance")
    worksheet.write(0,2,"Mean")
    worksheet.write(0,3,"Worst")
    worksheet.write(0,4,"Time")
    
    sol=[]
    
    for inst in range(len(instances)):
        
        for k in depths:
            
            for p in postprocessing:
                
                val=[]
                r_time=[]
                    
                trainfiles, testfiles = create_train_and_test(instances[inst]+".csv",1,DIR)
                
                for nbr_test in range(len(testfiles)):
                                                
                        trainfile=trainfiles[nbr_test]
                        testfile=testfiles[nbr_test]
                
                        a=time.time()
                        
                        tree, C_set = main(["-f"+trainfile,"-d "+str(k),"-p "+str(p),"-a"+algo,"-t"+str(tl)])
                        
                        real_time = time.time() - a
                        
                        score=test(tree,C_set,testfile)
                        
                        sol.append((instances[inst].split("\\")[-1],k,nbr_test,score,p,real_time))
                        
                        val.append(score)
                        
                        r_time.append(real_time)
                        
                write_in_excel(worksheet,len(instances)*k+inst,instances[inst].split("\\")[-1],val,r_time)
        
    workbook.close()
            
    return sol

def write_in_excel(worksheet,count,name,val,r_time):
    """ Write a piece of information in a a worksheet
    
    Input:
        worksheet (worksheet): worksheet on which the info has to be written
        count (integer): index of the row in which the info has to be written
        name (string): name of the instance
        val (list of floats): accuracy in the tests
        r_time (list of floats): time to run the tests
        
    Output:
        none
    """
        
    worksheet.write(count+1,1,name)
    worksheet.write(count+1,2,str(100*round(np.mean(val),3)))
    worksheet.write(count+1,3,str(100*round(np.min(val),3)))
    worksheet.write(count+1,4,str(round(np.mean(r_time),2)))
    
def run_CART(instances,depths):
    """ Run testing method with CART and write it in a xlsx file
    
    Input:
        instances (list of string): names of the instances
        depths (list of integers): maximum depths to be considered
        
    Output:
        sol (list of multi type): diverse information about the results
    """
    
    sol=[]
    val=[]
    r_time=[]
    workbook = xlsxwriter.Workbook('RUN.xlsx')
    worksheet = workbook.add_worksheet()
    worksheet.write(0,1,"Instance")
    worksheet.write(0,2,"Mean")
    worksheet.write(0,3,"Worst")
    worksheet.write(0,4,"Time")
    
    sol=[]
    
    for inst in range(len(instances)):
                
        for k in depths:
                            
            val=[]
            r_time=[]
                
            trainfiles, testfiles = create_train_and_test(instances[inst]+".csv",1,DIR)
            
            for nbr_test in range(len(testfiles)):
                                            
                trainfile=trainfiles[nbr_test]
                testfile=testfiles[nbr_test]
        
                a=time.time()
                
                score=genCART(trainfile,testfile,k)
                                
                real_time = time.time() - a
                                    
                sol.append((instances[inst].split("\\")[-1],k,nbr_test,score,real_time))
                
                val.append(score)
                
                r_time.append(real_time)
                    
            write_in_excel(worksheet,len(instances)*k+inst,instances[inst].split("\\")[-1],val,r_time)
            
    try:
    
        workbook.close()
        
    except:
        
        print("Please close RUN.xlsx")
        
        input()
        
        workbook.close()
            
    return sol
    
    
CURDIR=os.getcwd()
DIR=CURDIR+"\Instances\\"   
ALL_INSTANCES=["iris","IndiansDiabetes","banknote","balance-scale","monk1","monk2","monk3","Ionosphere","spambase","car_evaluation","biodeg"
               ,"seismic_bumps","Statlog_satellite","tic-tac-toe","wine"]
BIG_INSTANCES=["magic04","default_credit","HTRU_2","letter_recognition","Statlog_shuttle","hand_posture"]
instances=[DIR+i for i in ALL_INSTANCES[13:15]]
postprocessing=[0]
depths = [2]
timelimit=10*60
algo="CG"



final_tree, C_set = main(["-f"+DIR+"iris.csv","-d 2","-p 0","-aCG","-t600"])
#sol=run_tests(instances,depths,postprocessing,algo,timelimit)
#sol=run_CART(instances,depths)
