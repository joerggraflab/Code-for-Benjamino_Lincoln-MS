from pyfann import libfann as lf
import csv
import sys
import os
from pprint import pprint as pr
#++++++++++     
basedir = os.path.dirname(__file__)
clib = '../lib/python/'
sys.path.append(os.path.join(basedir, clib))
#++++++++++
import heatmap_generator as hmg
import analysis as an
import cPickle as pickle
import numpy as np
import csv
import data_parser

global names_location, save_path, inputs_location, test_location
save_path = "../figures/order_all_averaged_fixed/"
names_location = "../data/names/order_all_averaged_fixed.txt"
net_location = "../data/networks/order_all_averaged_fixed.net"
inputs_location = "../data/Dataset/Testing/Inputs/inputs.csv"
test_location = "../data/Dataset/Testing/Tests/"
def create_and_save(scaling=False):
    '''
    Creates and saves a heatmap if sys.argv[1] = create
    '''


    # Load the saved neural net
    ann = lf.neural_net()
    ann.create_from_file(net_location)

    # Get the names, put into array
    names_list = [line.rstrip('\n') for line in open(names_location)]
    #print names_list
    # Get inputs to create heat array with
    with open(inputs_location) as f:
        inputs_csv = csv.reader(f, delimiter=',')
        inputs = [float(i) for i in inputs_csv.next()]
    #Create
    heatmap = hmg.create_heat_map(ann, inputs, names_list, bias=False, save_path=save_path, scaling = False)
    #Save
    hmg.save_heatmap_array(heatmap, "order.p")

    return heatmap

def main():

    # Load neural network 
    ann = lf.neural_net()
    ann.create_from_file(net_location)

    # Replace this nonsense with argparse later on
    # But for now, we live in anarchy
    
    # Create or load heatmap based on ANN
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'create':
        heatmap = create_and_save(scaling=False)
    elif len(sys.argv) > 1 and sys.argv[1].lower() == 'load':   #load from file
        heatmap = pickle.load(open(os.path.join(basedir, '../data/heatmaps/order.p'),'rb'))
    else:
        print "Please input a valid argument to {0}, either `create` or `load`.\nIf running for the first time, pick `create`".format(sys.argv[0])
        sys.exit(1)
    
    Heatmap = hmg.Heatmap(heatmap)
    Heatmap.get_row_avgs()
    Heatmap.get_col_avgs()


    names_list = [line.rstrip('\n') for line in open(names_location)]
    names_dict = {}     # key=name, value=index
    for i,v in enumerate(names_list):
        names_dict[v] = str(i)
    rmse, bray_curtis = an.test_network(ann, test_location, save_path)
    # Now we have the heatmap object so lets do some stuff
    g = an.create_fuzzy_hairball(Heatmap, save_path) 
    # Create heatmap value csv
    heatmap_csv = csv.writer(open("heatmap_values.csv", 'w'), delimiter=',')
    heatmap_csv.writerow([""]+names_list[0:-6])
    for i,v  in enumerate(Heatmap.heatmap):
        heatmap_csv.writerow([names_list[i]] + [str(s) for s in v])


    in_degree_dict = an.get_degrees(g, names_list, "in")
    out_degree_dict = an.get_degrees(g, names_list, "out")
    total_degree_dict = an.get_degrees(g, names_list, "all")
    
    with open('degrees.csv', 'w') as degree_csv_filehandle:
        degree_csv = csv.writer(degree_csv_filehandle)
        degree_csv.writerow(['Taxon', 'In', 'Out', 'Total'])
        for k in total_degree_dict.keys():
            ins = str(in_degree_dict[k])
            outs = str(out_degree_dict[k])
            total = str(total_degree_dict[k])
            degree_csv.writerow([k, ins, outs, total])

    # Get top ten most connected and create fuzzy hairball (connectivity network)
    top_ten = an.create_topten_bar(total_degree_dict, save_path, names_dict)
    g = an.create_fuzzy_hairball_fixed(Heatmap, save_path, 10, total_degree_dict, names_list)

    np.set_printoptions(precision=4)
    print "RMSE: {}\n".format(rmse)
    print "BC: {}".format(bray_curtis)

if __name__ == "__main__":
    main()
