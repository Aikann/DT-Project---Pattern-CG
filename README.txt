"""Decision tree project"""

"""Authors"""

Guillaume Crognier, Ecole polytechnique (Paris, France), guillaume.crognier@polytechnique.edu
Murat Firat, Eindhoven University of Technology (Eindhoven, The Netherlands), m.firat@tue.nl
Adriana F. Gabor, United Arab Emirates University (Al Ain, United Arab Emirates), adriana.gabor@uaeu.ac.ae
Yingqian Zhang, Eindhoven University of Technology (Eindhoven, The Netherlands), yqzhang@tue.nl

"""Acknowledgement"""

Cor Hurkens, Eindhoven University of Technology (Eindhoven, The Netherlands)

"""Developer"""

Guillaume Crognier, Ecole polytechnique (Paris, France), guillaume.crognier@polytechnique.edu

"""Requirements"""

Python 2.7 and a full version of Cplex have to be installed (should work on Python 3.x with possibly minor changes).
The cplex module in Python has to be installed with the full version of cplex (see https://www.ibm.com/support/knowledgecenter/SSSA5P_12.7.1/ilog.odms.cplex.help/CPLEX/GettingStarted/topics/set_up/Python_setup.html).

"""Tested machine"""

Windows 10
Python 2.7 (Anaconda distribution)
Cplex 12.7.1

"""Getting started"""

From a Python environment such as Spyder:

	Single run (only build the tree, based on the full dataset):

		In main.py, at the end of the file, comment the lines with run_tests and run_cart in it.
		Uncomment the line above these two. Example:

		tree, C_set = main(["-f"+DIR+"iris.csv","-d 3","-p 0","-aCG","-t600"])
		#sol,val, r_time=run_tests(instances,depths,postprocessing,algo,timelimit)
		#sol,val, r_time=run_CART(instances,depths)

	Multiple run (build tree on 50% of the dataset, test it on 25%, repeat 5 times):

		#tree, C_set = main(["-f"+DIR+"iris.csv","-d 3","-p 0","-aCG","-t600"])
		sol,val, r_time=run_tests(instances,depths,postprocessing,algo,timelimit)
		#sol,val, r_time=run_CART(instances,depths)

You can also run it from a command line if you add the following code:

	if __name__ == "__main__":
   		main(sys.argv[1:])

"""Parameters of the main function"""

-f (string) file name. The file should be in the "Instances" folder and should correspond to a usual csv format, separated
   by ";" or by columns (see the examples in the folder).

-d (int) max depth of the tree.

-p (int) Post-processing method (unused). Leads to overfitting trees. 0 means no post-processing. If you want to use it anyway, you may need
	 additional requirements (if you want to use it contact guillaume.crognier@polytechnique.edu).

-a (string) Type of algorithm. Should be "CG" in this version. If you are interesting in post-processing, you may change this.

-t (int) Time limit, in seconds.

"""Output"""

tree is a list of patterns (see pattern.py). Contains all the information about the constructed tree.

C_set is a 3D list containing the thresholds used in the algorithm.

sol contains some basic results.

"""More information"""

Please read the corresponding paper [MISSING REF].