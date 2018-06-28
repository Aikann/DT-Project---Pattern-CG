# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 09:51:47 2018

@author: Guillaume
"""
import os
from learn_tree_funcs import read_file, write_file
import regtrees2 as tr
import time

def write_C_pb(filename,depth):
    
    fr=open('bf.c','r')
    
    fw=open('brute_force.c','w')
    
    for line in fr.readlines():
        
        if "int TreeDep = " in line:
            
            fw.write("int TreeDep = "+str(depth)+";\n")
            
        elif 'readSampleFile("myfile")' in line:
            
            fw.write('readSampleFile("'+filename+'.csv");')
            
        elif 'FILE *f = fopen("file.txt", "w");' in line:
            
            fw.write('FILE *f = fopen("results_brute_force.txt", "w");\n')
            
        else:
            
            fw.write(line)
            
    fw.close()
    fr.close()

def write_C_subp(l,depth):
    
    fr=open('bf.c','r')
    
    fw=open('subp'+str(l)+'.c','w')
    
    for line in fr.readlines():
            
        if "int TreeDep =" in line:
            
            fw.write("int TreeDep = "+str(depth)+";\n")
            
        elif 'readSampleFile("myfile")' in line:
            
            fw.write('readSampleFile("sub_p_'+str(l)+'.csv");')
            
        elif 'FILE *f = fopen("file.txt", "w");' in line:
            
            fw.write('FILE *f = fopen("results_subp_'+str(l)+'.txt", "w");\n')
            
        else:
            
            fw.write(line)
            
    fw.close()
    fr.close()
    
def execute_C_code(l,bruteforce=False):
    
    fw=open('run.cmd','w')
    
    cwd = os.getcwd()
    
    fw.write('@echo off\n')
    fw.write('cd '+cwd+"\n")
    disk=cwd.split(':')[0]
    fw.write(disk+':\n')
    
    if bruteforce:
        
        fw.write('gcc brute_force.c -o bf\n')
        fw.write('bf\n')
        
    else:
        
        fw.write('gcc subp'+str(l)+'.c -o subp'+str(l)+'\n')
        fw.write('subp'+str(l)+'\n')
    
    fw.close()
        
    os.popen('run.cmd').read()
    
def get_res(l,bruteforce=False):
    
    if bruteforce:
        
        fr=open('results_brute_force.txt',"r")
        
        res = int(fr.readline().split('\n')[0])
        
        fr.close() 
        
    else:    
    
        fr=open('results_subp_'+str(l)+'.txt',"r")
        
        res = int(fr.readline().split('\n')[0])
        
        fr.close()
    
    return res

def brute_force_solver(inputfile,depth):
    
    a=time.time()
    
    read_file(inputfile)
    
    write_file(inputfile+".transformed")
   
    tr.df = tr.get_data(inputfile+".transformed")
            
    filename='brute_force_'+inputfile
    
    tr.df[tr.df.columns[-1]]=tr.df[tr.df.columns[-1]].astype('int')
    
    tr.df.to_csv(filename,sep=',',index=False,header=False)
    
    write_C_pb(filename,depth)
    
    execute_C_code(0,True)
    
    res = get_res(0,True)
    
    print("Optimal solution found: "+str(res))
    
    print("Full time: "+str(time.time()-a))
    
def get_new_thresholds(l,depth):
    
    fr=open('results_subp_'+str(l)+'.txt',"r")
    
    readl=fr.readlines()
    
    fr.close()
    
    if depth==2:
    
        line0, line1, line2 = readl[2], readl[3], readl[4]
        
        i0 = int(line0.split('Feat_')[1].split(',')[0])
        
        thr0 = float(line0.split('threshold ')[1].split('\n')[0])
        
        j0 = 1 + 4*l
        
        i1 = int(line1.split('Feat_')[1].split(',')[0])
        
        thr1 = float(line1.split('threshold ')[1].split('\n')[0])
        
        j1 = 4*l
        
        i2 = int(line2.split('Feat_')[1].split(',')[0])
        
        thr2 = float(line2.split('threshold ')[1].split('\n')[0])
        
        j2 = 4*l + 2
        
        new_thr = [(j0,i0,thr0),(j1,i1,thr1),(j2,i2,thr2)]
        
    elif depth==1:
        
        line0 = readl[2]
        
        i0 = int(line0.split('Feat_')[1].split(',')[0])
        
        thr0 = float(line0.split('threshold ')[1].split('\n')[0])
        
        j0 = 2*l
        
        new_thr = [(j0,i0,thr0)]
    
    return new_thr