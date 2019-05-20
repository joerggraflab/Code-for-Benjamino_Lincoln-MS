from pprint import pprint as p
import csv
import os
import sys
import random
from pyfann import libfann as lf
from math import ceil as roundup
import numpy as np
from sklearn.metrics import mean_absolute_error

def create_data_array(file_location, num_envs):
    '''
    Creates datafile for vaidation purposes given a file_location
    '''

    # Set variables and init
    name_array = []
    dataset_count = 0
    out_start = 0
    data_array = []

    # Loop through CSVs, get training data and create data file
    for fn in os.listdir(file_location):
        counter = 0
        try:
            f = open(os.path.join(file_location, fn))
        except:
            print "CSVs dont exist"
            sys.exit(1)
        csv_reader = csv.reader(f, delimiter=',')
        next(csv_reader, None) # skip headers
        row_count = 0
        sub_array = []
        for row in csv_reader:
            row_count += 1
            counter += 1
            values = row[1:]
            num_cols = len(values)
            sub_array.append(values)
        f.close()
        sub_array = zip(*sub_array)

        i = 0
        while i < num_cols - 1:
            inputs = sub_array[i]
            targets = sub_array[i+1][0:len(inputs)-num_envs]
            data_array.append((inputs, targets))
            i += 1
    return data_array

def chunkify(lst,n):
    '''
    Splits up dataset into n chunks for nfold cross validation
    '''
    return [lst[i::n] for i in xrange(n)]

def train_ann(training_set):
    '''Train the anni
    '''
    #Constants
    total_datapoints = len(training_set)
    num_inputs = len(training_set[0][0])
    num_outputs = len(training_set[0][1])

    learning_rate = 0.01
    momentum = 0.95
    desired_error = 0.0001
    iterations_between_reports = 100
    maximum_iterations = 10000
    num_hiddens1 = roundup(num_inputs*0.95)
    num_hiddens2 = roundup(num_inputs*0.85)

    #Gotta make a training data file
    data_file = "../data/validation/training.data" 
    f = open(data_file, 'w')
    f.write("%s %s %s\n" % (total_datapoints, num_inputs, num_outputs))
    for datapoint in training_set:
        inp = ' '.join(str(x) for x in datapoint[0])
        targ = ' '.join(str(x) for x in datapoint[1])
        f.write("%s\n" % inp)
        f.write("%s\n" % targ)
    f.close()

    mse = 1
    while mse > desired_error:
        ann = lf.neural_net()
        ann.create_standard_array([num_inputs, num_hiddens1, num_hiddens2, num_outputs])
        ann.set_learning_rate(learning_rate)
        ann.set_learning_momentum(momentum)
        ann.set_activation_function_hidden(lf.SIGMOID_SYMMETRIC)  #This is to ensure negative and positive influences can be detected
        ann.set_activation_function_output(lf.SIGMOID)	#Ensure output isnt negative
        ann.set_bit_fail_limit(0.01)
        #ann.set_train_error_function(lf.ERRORFUNC_TANH)

        # Train
        ann.train_on_file(data_file, maximum_iterations, iterations_between_reports, desired_error)
        mse = ann.get_MSE()

    return ann

def test_ann(ann, test_set):
    '''Test ann with test set
    '''
    
    rmses = []
    for datapoint in test_set:
        inputs = [float(x) for x in datapoint[0]]
        targets = [float(x) for x in datapoint[1]]
        test_outputs = ann.run(inputs)
        #rmse = np.sqrt(np.mean((np.array(targets)-np.array(test_outputs))**2))
        rmse = mean_absolute_error(targets, test_outputs)
        rmses.append(rmse)
    rmse = np.mean(rmses)
    return rmse

def perform_validation(data_array):
    '''Performs cross validation
    '''
    #First split into chunks for training/test sets
    chunks = chunkify(data_array, 10)
    rmses = []
    for i in range(10):
        training_set = [x for e,x in enumerate(chunks) if e!=i]
        training_set = [q for w in training_set for q in w]
        test_set = chunks[i]
        try:
            ann = train_ann(training_set)
        except Exception as e:
            print e
            sys.exit()
        rmse = test_ann(ann, test_set)
        rmses.append(rmse)
    rmse = np.mean(rmses)

    return rmse

def main():
    file_location = "../data/Dataset/All_Averaged"
    data_file = "../data/training/order_all_averaged_fixed.data"
    f = open(data_file, 'r')
    info = (f.readline()).split(' ')
    num_inputs = int(info[1])
    num_outputs = int(info[2])
    num_envs = num_inputs - num_outputs
    f.close()
    data_array = create_data_array(file_location, num_envs)
    # For each iteration of validaton
    rmses = []
    # Loop 100 times, split up data into training and validation sets
    # Perform validation and note rmse
    for i in range(100):
        random.shuffle(data_array)
        rmses.append(perform_validation(data_array))
    print "10 fold cross validation rmse: %s" % np.mean(rmses)

if __name__ == "__main__":
    main()

