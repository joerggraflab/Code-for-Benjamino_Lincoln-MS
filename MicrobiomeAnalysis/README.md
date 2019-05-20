TermiteANN
==========

Author: Stephen Lincoln

University of Connecticut

Department of Chemical and Biomolecular Engineering

# Synopsis

These scripts utilize Python and third party libraries to create, train, test, and analyze a neural network to better understand taxa-taxa and taxa-environment relationships within a microbiome. This data consists of time-course data (usually days 0, 1, 2, 3, 5, 7, 14, 21, 28, 35, 42, 49) of the abundance of ~135 micro-organsisms. The trained network is then tested for interpolation and species-interactions; in other words, it can be used to predict how each bacteria's abundance will change over time given a certain type of food source (birch, oak, original stock, cardboard, spruce, maple, as well as no food).  It also allows one to view direct and indirect relationships within the microbiome.

Each input node is representative of a microorganism type or type of food source. Sensitivity analysis on the network can be performed by changing each input node one at a time on a range of values, usually 90% to 110% of the original, and comparing the output of the network to the original output while keeping all other input nodes constant. This process is repeated for each input node. From here, we can observe how each speicies changes with each other and see what species play important factors in the community as a whole with heat maps and connectivity networks.

This project utilizes Python 2.7 with multiple 3rd-party libraries that must be installed. The easiest way would be to install [Anaconda](http://continuum.io/downloads), which includes SciPy, NumPy, and Matplotlib, and a bunch of other commonly used libraries. These libraries can also be installed manually, and some do not come with Anaconda. The requirements include:
* [FANN](http://leenissen.dk/fann/wp/) with Python Bindings (available from v2.1, or sudo apt-get install python-pyfann after installing FANN)
* [SciPy](http://www.scipy.org/)
* [NumPy](http://www.numpy.org/)
* [Matplotlib](http://matplotlib.org/)
* [Graph Tools](http://graph-tool.skewed.de/)

NOTE!: If you install pyfann from apt-get, you must install it as root in /usr/lib/pymodules/python2.7/pyfann/. Therefore, you must allow this directory to be run by non-root users. Easiest (but not most secure) way is sudo chmod 644 /usr/lib/pymodules/python2.7/pyfann/. You'll also have to append this directory to your $PYTHONPATH

# How To

The methodology behind this project follows as such:
1. Format CSV files in the correct format (Column 1 is the species/food source, following columns are time point abundance data, headers must be in the dataset)
2. Specify csv directory and .data file you wish to create
3. Create the data file based on CSV's
4. Create the ANN, train on the .data file
5. ANN Analysis to generate heat map and species-connectivity map

In order to run with your own data:
1. Place each CSV you wish to train on in data/Dataset/Averaged/Train/ - Make sure that all CSV's have the same headers and row names in the same order, and the non-taxa data (food sources, environmental variables, etc) are the last rows in the CSV files.
2. Edit lib/python/data_parser.py:39 and change '6' to the number of food sources/environmental variables in your dataset(s)
3. For each CSV, take out a random timepoint or two. Split the CSV into 2 CSV's and put them into data/Dataset/Tests/.   Put one of the random timepoints taken out, as well as the timepoint data ahead of it, into data/Dataset/Testing/Inputs/inputs.csv, transposed, without any headers or labels.
4. If you wish to perform 10x cross validation on your dataset to test parameters, edit scripts/10foldxval.py:65-71,90-91 and run it
5. Edit parameters in scripts/ann.py:30-37,44-45 to your liking.
6. cd into scripts, and run `python ann.py`
7. Run `python analyze_ann.py create`

In the heatmap, each row and column is a number, associated with a certain species (or food source, in the last 6 rows/columns).

# TODO
1. Refactor codebase
2. Create main script to incorperate the whole process
3. Clean up variables
