# -*- coding: utf-8 -*-
"""
Created on Thu Jul 19 14:25:38 2018

@author: Guillaume
"""

from __future__ import print_function

import os
import subprocess

from time import time
from operator import itemgetter
from scipy.stats import randint

import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import export_graphviz
from sklearn.grid_search import GridSearchCV
from sklearn.grid_search import RandomizedSearchCV
from sklearn.cross_validation import  cross_val_score
from sklearn.cross_validation import train_test_split
import xlsxwriter


def get_code(tree, feature_names, target_names,
             spacer_base="    "):
    """Produce pseudo-code for decision tree.

    Args
    ----
    tree -- scikit-leant Decision Tree.
    feature_names -- list of feature names.
    target_names -- list of target (class) names.
    spacer_base -- used for spacing code (default: "    ").

    Notes
    -----
    based on http://stackoverflow.com/a/30104792.
    """
    left      = tree.tree_.children_left
    right     = tree.tree_.children_right
    threshold = tree.tree_.threshold
    features  = [feature_names[i] for i in tree.tree_.feature]
    value = tree.tree_.value

    def recurse(left, right, threshold, features, node, depth):
        spacer = spacer_base * depth
        if (threshold[node] != -2):
            print(spacer + "if ( " + features[node] + " <= " + \
                  str(threshold[node]) + " ) {")
            if left[node] != -1:
                    recurse (left, right, threshold, features,
                             left[node], depth+1)
            print(spacer + "}\n" + spacer +"else {")
            if right[node] != -1:
                    recurse (left, right, threshold, features,
                             right[node], depth+1)
            print(spacer + "}")
        else:
            target = value[node]
            for i, v in zip(np.nonzero(target)[1],
                            target[np.nonzero(target)]):
                target_name = target_names[i]
                target_count = int(v)
                print(spacer + "return " + str(target_name) + \
                      " ( " + str(target_count) + " examples )")

    recurse(left, right, threshold, features, 0, 0)


def visualize_tree(tree, feature_names, fn="dt"):
    """Create tree png using graphviz.

    Args
    ----
    tree -- scikit-learn Decision Tree.
    feature_names -- list of feature names.
    fn -- [string], root of filename, default `dt`.
    """
    dotfile = fn + ".dot"
    pngfile = fn + ".png"

    with open(dotfile, 'w') as f:
        export_graphviz(tree, out_file=f,
                        feature_names=feature_names)

    command = ["dot", "-Tpng", dotfile, "-o", pngfile]
    try:
        subprocess.check_call(command)
    except:
        exit("Could not run dot, ie graphviz, "
             "to produce visualization")


def encode_target(df, target_column):
    """Add column to df with integers for the target.

    Args
    ----
    df -- pandas Data Frame.
    target_column -- column to map to int, producing new
                     Target column.

    Returns
    -------
    df -- modified Data Frame.
    targets -- list of target names.
    """
    df_mod = df.copy()
    targets = df_mod[target_column].unique()
    map_to_int = {name: n for n, name in enumerate(targets)}
    df_mod["Target"] = df_mod[target_column].replace(map_to_int)

    return (df_mod, targets)


def get_iris_data():
    """Get the iris data, from local csv or pandas repo."""
    if os.path.exists("iris.csv"):
        print("-- iris.csv found locally")
        df = pd.read_csv("iris.csv", index_col=0)
    else:
        print("-- trying to download from github")
        fn = ("https://raw.githubusercontent.com/pydata/"
              "pandas/master/pandas/tests/data/iris.csv")
        try:
            df = pd.read_csv(fn)
        except:
            exit("-- Unable to download iris.csv")

        with open("iris.csv", 'w') as f:
            print("-- writing to local iris.csv file")
            df.to_csv(f)

    return df

def report(grid_scores, n_top=3):
    """Report top n_top parameters settings, default n_top=3.

    Args
    ----
    grid_scores -- output from grid or random search
    n_top -- how many to report, of top models

    Returns
    -------
    top_params -- [dict] top parameter settings found in
                  search
    """
    top_scores = sorted(grid_scores,
                        key=itemgetter(1),
                        reverse=True)[:n_top]
    for i, score in enumerate(top_scores):
        print("Model with rank: {0}".format(i + 1))
        print(("Mean validation score: "
               "{0:.3f} (std: {1:.3f})").format(
               score.mean_validation_score,
               np.std(score.cv_validation_scores)))
        print("Parameters: {0}".format(score.parameters))
        print("")

    return top_scores[0].parameters

def run_gridsearch(X, y, clf, param_grid, cv=5):
    """Run a grid search for best Decision Tree parameters.

    Args
    ----
    X -- features
    y -- targets (classes)
    cf -- scikit-learn Decision Tree
    param_grid -- [dict] parameter settings to test
    cv -- fold of cross-validation, default 5

    Returns
    -------
    top_params -- [dict] from report()
    """
    grid_search = GridSearchCV(clf,
                               param_grid=param_grid,
                               cv=cv)
    start = time()
    grid_search.fit(X, y)

    print(("\nGridSearchCV took {:.2f} "
           "seconds for {:d} candidate "
           "parameter settings.").format(time() - start,
                len(grid_search.grid_scores_)))

    top_params = report(grid_search.grid_scores_, 3)
    return  top_params

def run_randomsearch(X, y, clf, param_dist, cv=5,
                     n_iter_search=20):
    """Run a random search for best Decision Tree parameters.

    Args
    ----
    X -- features
    y -- targets (classes)
    cf -- scikit-learn Decision Tree
    param_dist -- [dict] list, distributions of parameters
                  to sample
    cv -- fold of cross-validation, default 5
    n_iter_search -- number of random parameter sets to try,
                     default 20.

    Returns
    -------
    top_params -- [dict] from report()
    """
    random_search = RandomizedSearchCV(clf,
                        param_distributions=param_dist,
                        n_iter=n_iter_search)

    start = time()
    random_search.fit(X, y)
    print(("\nRandomizedSearchCV took {:.2f} seconds "
           "for {:d} candidates parameter "
           "settings.").format((time() - start),
                               n_iter_search))

    top_params = report(random_search.grid_scores_, 3)
    return  top_params

def write_in_excel(worksheet,count,name,val,r_time):
        
    worksheet.write(count+1,1,name)
    worksheet.write(count+1,2,str(100*round(np.mean(val),3)))
    worksheet.write(count+1,3,str(100*round(np.min(val),3)))
    worksheet.write(count+1,4,str(round(np.mean(r_time),2)))



def call(n,k,instance):
    
    df = pd.read_csv(DIR+instance+".csv",sep=';')

    features = df.columns[0:len(df.columns)-1]
    df, targets = encode_target(df, df.columns[-1])
    y = df["Target"]
    X = df[features]
    
    X_train, X_test, y_train, y_test = train_test_split(X,y,train_size=0.5,test_size=0.25,random_state=10*n)  
            
    
    print("-- 10-fold cross-validation "
          "[using setup from previous post]")
    dt_old = DecisionTreeClassifier(min_samples_split=20,
                                    random_state=99,max_depth=k)
    dt_old.fit(X_train, y_train)
    scores = cross_val_score(dt_old, X_train, y_train, cv=10)
    print("mean: {:.3f} (std: {:.3f})".format(scores.mean(),
                                              scores.std()),
                                              end="\n\n" )
    
    print("-- Grid Parameter Search via 10-fold CV")
    
    # set of parameters to test
    param_grid = {"criterion": ["gini", "entropy"],
                  "min_samples_split": [0.02,0.05,0.1,0.2],
                  "max_depth": [k],
                  "class_weight": [None,"balanced"],
                  "min_samples_leaf": [1, 0.01, 0.05, 0.1, 0.2],
                  }
    
    dt = DecisionTreeClassifier(max_depth=k)
    ts_gs = run_gridsearch(X_train, y_train, dt, param_grid, cv=10)
    
    print("\n-- Best Parameters:")
    for k, v in ts_gs.items():
        print("parameter: {:<20s} setting: {}".format(k, v))
        
    print("\n\n-- Testing best parameters [Grid]...")
    dt_ts_gs = DecisionTreeClassifier(**ts_gs)
    scores = cross_val_score(dt_ts_gs, X_train, y_train, cv=10)
    print("mean: {:.3f} (std: {:.3f})".format(scores.mean(),
                                              scores.std()),
                                              end="\n\n" )
    
    
    print("\n-- get_code for best parameters [Grid]:", end="\n\n")
    dt_ts_gs.fit(X_train,y_train)
    get_code(dt_ts_gs, features, targets)
    
    final_score = sum(dt_ts_gs.predict(X_test) == y_test)/float(len(X_test))
    
    return final_score

print("\n-- get data:")
CURDIR=os.getcwd()
DIR=CURDIR+"\Instances\\"
ALL_INSTANCES=["iris","IndiansDiabetes","banknote","balance-scale","monk1","monk2","monk3","Ionosphere","spambase","car_evaluation","biodeg"
               ,"seismic_bumps","Statlog_satellite","tic-tac-toe","wine"]
BIG_INSTANCES=["magic04","default_credit","HTRU_2","letter_recognition","Statlog_shuttle","hand_posture"]
k=4

workbook = xlsxwriter.Workbook('RUN.xlsx')
worksheet = workbook.add_worksheet()
worksheet.write(0,1,"Instance")
worksheet.write(0,2,"Mean")
worksheet.write(0,3,"Worst")
worksheet.write(0,4,"Time")

sol=[]
c=0

for instance in BIG_INSTANCES:
    
    c+=1

    all_results=[]
    times=[]
    val=[]
    
    for n in range(5):
        
        a=time()
        
        final_score = call(n,k,instance)
        
        times.append(time()-a)
        
        sol.append((instance,k,n,final_score,times[-1]))
        
        val.append(final_score)
                        
    write_in_excel(worksheet,len(ALL_INSTANCES)*k+c,instance,val,times)
        
workbook.close()