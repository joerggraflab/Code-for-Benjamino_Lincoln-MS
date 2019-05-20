from pyfann import libfann as lf
import sys
sys.path.append("../lib/python/")
import data_parser
from math import ceil as roundup

# First, create the .data files that we need to train on

csv_location = "../data/Dataset/Averaged/Train"
data_file = "../data/training/order_all_averaged_fixed.data"
name_file = "../data/names/order_all_averaged_fixed.txt"

# create the data files from csv's in directory using our parser
data_parser.create_data_file(csv_location, data_file, name_file, bias=False, scaling=False)

##########################

# Now create and train the network


saved_net_file = "../data/networks/order_all_averaged_fixed.net"
## Grab the number of inputs, outputs (first line of .data in format #datapoints, inputs, outputs)
f = open(data_file, 'r')
info = (f.readline()).split(' ')
num_inputs = int(info[1])
num_outputs = int(info[2])
f.close()
## Settings
learning_rate = 0.1
momentum = 0.95
desired_error = 0.00001
iterations_between_reports = 100
maximum_iterations = 10000
## Determine number of hidden nodes
num_hiddens1 = roundup(num_inputs*0.95)
num_hiddens2 = roundup(num_inputs*0.85)

# Create network
ann = lf.neural_net()
ann.create_standard_array([num_inputs, num_hiddens1, num_hiddens2, num_outputs])
ann.set_learning_rate(learning_rate)
ann.set_learning_momentum(momentum)
ann.set_activation_function_hidden(lf.SIGMOID_SYMMETRIC)  #This is to ensure negative and positive influences can be detected
ann.set_activation_function_output(lf.SIGMOID)	#Ensure output isnt negative
ann.set_bit_fail_limit(0.01)

# Train
ann.train_on_file(data_file, maximum_iterations, iterations_between_reports, desired_error)
ann.save(saved_net_file)

