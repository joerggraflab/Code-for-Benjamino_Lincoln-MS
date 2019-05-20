from collections import OrderedDict
import matplotlib as ml
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import graph_tool.draw as gtd
import graph_tool.stats as gts
import graph_tool as gt
import scipy.spatial as sp
import numpy as np
import csv
import os
import sys
from numpy import log2
import csv

def test_network(ann, inputs_location, save_path):
    output_dir = '../data/Dataset/Testing/Results/'
    rmses = []
    bcs = []
    for root, dirs, filenames in os.walk(inputs_location):
        for fn in filenames:
            with open(inputs_location + fn, 'r') as f:
                inputs_csv = csv.reader(f, delimiter=',')
                inputs = [float(i) for i in inputs_csv.next()]
                outputs = [float(i) for i in inputs_csv.next()[0:-6]]
                test_outputs = ann.run(inputs)
                try:
                    rmses.append(np.sqrt(np.mean((np.array(outputs)-np.array(test_outputs))**2)))
                    bcs.append(sp.distance.braycurtis(np.array(outputs), np.array(test_outputs)))
                except Exception as e:
                    print e
                    print fn
                with open(output_dir + fn, 'w') as v:
                    outputs_csv = csv.writer(v, delimiter=',')
                    outputs_csv.writerow(outputs)
                    outputs_csv.writerow(test_outputs)
    rmse = np.mean(rmses)
    bray_curtis = np.mean(bcs)
    return rmse, 1-bray_curtis



def create_fuzzy_hairball(Heatmap, save_path, top=None):
    '''Creates connectivity network based on heatmap class
    If top is passed into the function, we will highlight the top nodes'''
    g = gt.Graph()
    g.add_vertex(int(len(Heatmap.heatmap)))
    file_name = "fuzzy_hairball.pdf"

    #Init vertex propertys
    vprop_label = g.new_vertex_property("string")
    vprop_vertex_color = g.new_vertex_property("string")
    #vprop_halo_color = g.new_vertex_property("string")
    #vprop_halo = g.new_vertex_property("bool")
    vprop_halo_size = g.new_vertex_property("float")
    #vprop_color = g.new_vertex_property("string")
    eprop_color = g.new_edge_property("string")

    edge_colors = []

    total_avg = np.absolute(Heatmap.heatmap).mean()
    total_std = np.absolute(Heatmap.heatmap).std()
    
    for i in range((len(Heatmap.heatmap))):
        vprop_label[g.vertex(i)] = str(i)
        vprop_vertex_color[g.vertex(i)] = "gray"
        #vprop_color[g.vertex(i)] = "green"
    for row_num, row_val in enumerate(Heatmap.heatmap):
        for col_num, col_val in enumerate(Heatmap.heatmap[row_num]):
            row_std = np.absolute(Heatmap.heatmap[row_num]).std()
            row_avg = np.absolute(Heatmap.heatmap[row_num]).mean()
            col_stds = np.absolute(Heatmap.heatmap).std(0)
            col_avgs = np.absolute(Heatmap.heatmap).mean(0)
            #if row_num != col_num and abs(col_val) > row_avg*3:
            if row_num != col_num and abs(col_val) > total_avg + 3*total_std:   
                g.add_edge(g.vertex(row_num), g.vertex(col_num))
                if col_val >= 0:
                    edge_colors.append("blue")
                else:
                    edge_colors.append("red")
    counter = 0
    for e in g.edges():
        eprop_color[e] = edge_colors[counter]
        counter += 1

    # If you want to delete vertices with no edges comment this out
    #del_list = []
    #for v in g.vertices():
    #    if v.in_degree() == 0 and v.out_degree() == 0:
    #        del_list.append(v)
    #for v in reversed(sorted(del_list)):
    #    g.remove_vertex(v)
    pos = gtd.arf_layout(g, a=3)
    
    vprops = {  'text'      :   vprop_label,
                'fill_color':   vprop_vertex_color }
                #'color'     :   vprop_color         }
    eprops = {  'color' :   eprop_color, 'pen_width': 3*(246/1000)}

    full_path = os.path.join(save_path, file_name)
    gtd.graph_draw(g, pos=pos, output_size=(800,800), eprops=eprops, vprops=vprops, output=full_path)

    return g

def create_fuzzy_hairball_fixed(Heatmap, save_path, n, d, names):
    '''
    This is kinda weird because in order to find our most connected taxa, we need to make 
    our connectivity network first in order to find out whats connected to what
    so we can't highlight the top in real time, because we might want to change what we want to hightlight
    So were just going to make it twice until I make it more slick
    No one has to know though, it will be our secret.
    '''
    g = gt.Graph()
    g.add_vertex(int(len(Heatmap.heatmap)))
    file_name = "fuzzyhairball.png"
    halo_numbers = []
    #Init vertex propertys
    vprop_label = g.new_vertex_property("string")
    vprop_vertex_color = g.new_vertex_property("string")
    vprop_shape = g.new_vertex_property("string")
    vprop_halo_color = g.new_vertex_property("string")
    vprop_halo = g.new_vertex_property("bool")
    vprop_halo_size = g.new_vertex_property("float")
    #vprop_color = g.new_vertex_property("string")
    eprop_color = g.new_edge_property("string")
    #eprop_size = g.new_edge_proprty("float")
    edge_colors = []

    total_avg = np.absolute(Heatmap.heatmap).mean()
    total_std = np.absolute(Heatmap.heatmap).std()
    
    to_highlight = [str(i) for i in d.keys()[-n:]]

    for i in range((len(Heatmap.heatmap))):
        vprop_label[g.vertex(i)] = str(i)
        name = names[i]
        if name in to_highlight:
            vprop_vertex_color[g.vertex(i)] = "gold"
        else:
            vprop_vertex_color[g.vertex(i)] = "lightgrey"
        if int(i) in halo_numbers:
            #vprop_halo[g.vertex(i)] = True
            vprop_shape[g.vertex(i)] = "square"
        else:
            #`vprop_halo[g.vertex(i)] = False
            vprop_shape[g.vertex(i)] = "circle"
        #vprop_halo_color[g.vertex(i)] = "green"
        vprop_halo_size[g.vertex(i)] = 0.0
        vprop_halo[g.vertex(i)] = False
        #vprop_color[g.vertex(i)] = "green"
    for row_num, row_val in enumerate(Heatmap.heatmap):
        for col_num, col_val in enumerate(Heatmap.heatmap[row_num]):
            row_std = np.absolute(Heatmap.heatmap[row_num]).std()
            row_avg = np.absolute(Heatmap.heatmap[row_num]).mean()
            col_stds = np.absolute(Heatmap.heatmap).std(0)
            col_avgs = np.absolute(Heatmap.heatmap).mean(0)
            #if row_num != col_num and abs(col_val) > row_avg*3:
            if row_num != col_num and abs(col_val) > total_avg + 3*total_std:   
                g.add_edge(g.vertex(row_num), g.vertex(col_num))
                if col_val >= 0:
                    edge_colors.append("blue")
                else:
                    edge_colors.append("red")
    counter = 0
    for e in g.edges():
        eprop_color[e] = edge_colors[counter]
        counter += 1
    
    
    vprops = {  'text'      :   vprop_label,
                'font_size' :   45,
                'size'      :   85,
                'fill_color':   vprop_vertex_color,
                'halo'      :   vprop_halo,
                #'halo_color':   vprop_halo_color,
                #'halo' :   vprop_halo_size,
                'pen_width' :   0,
                'shape'     :   vprop_shape}
    #'color'     :   vprop_color         }
    eprops = {  'color' :   eprop_color, 'pen_width': 7.5}
    del_list = []
    for v in g.vertices():
        if v.in_degree() == 0 and v.out_degree() == 0:
            del_list.append(v)
    for v in reversed(sorted(del_list)):
        g.remove_vertex(v)
    pos = gtd.arf_layout(g, d=0.01, a=3, max_iter=0)
    #pos = gtd.sfdp_layout(g)
    full_path = os.path.join(save_path, file_name)
    try:
        gtd.graph_draw(g, pos=pos, bg_color=[1,1,1,1], output_size=(1200,1200), eprops=eprops, vprops=vprops, output=full_path, fmt="png")
    except Exception as e:
        print e
    return g

def get_degrees(g, names_list, direction="all"):
    '''
    Gets in and/or out degrees of each vertex based on direction arg
    dir = both, in, out
    defults to both
    '''
    counter = 0
    degree_dict = {}
    for v in g.vertices():
        name = names_list[counter]
        if direction == "in":
            degree_dict[name] = v.in_degree()
            #print name + " in: " + str(v.in_degree())
        elif direction == "out":
            degree_dict[name] = v.out_degree()
            #print name + " out: " + str(v.out_degree())
        elif direction == "all":
            degree_dict[name] = v.in_degree() + v.out_degree()
        else:
            print "You didn't use a valid direction"
        counter += 1

  
    degree_dict = OrderedDict(sorted(degree_dict.items(), key=lambda(k,v):(v,k)))
    
    return degree_dict

def create_topten_bar(d, save_path, names_dict):
    '''
    Displays the top ten species, in terms of overall connections, in bar format
    d is the dictionary of {name: degrees}
    '''

    fig, ax = plt.subplots()
    file_name = "topten.tiff"
    labelsizes = 14
    fig.set_size_inches(15.5,10.5)
    fig.set_dpi(600)
    #number of bars
    ind = np.arange(10)
    bar_width = 0.43
    #labels and values

    minor_ticks = np.arange(0, 20, 1)
    y_labels = tuple(str(names_dict[i] + '-' + str(i).split(';')[-1]) for i in d.keys()[-10:])
    #y_labels = tuple(str(i) for i in d.keys()[-10:])
    top_ten_values = tuple(int(i) for i in d.values()[-10:])
    #print y_labels
    #print top_ten_values 
    ax.barh(ind, top_ten_values, bar_width, color='black')
    plt.xlabel("Number of Connections")
    plt.ylabel("Taxa Order")
    ax.set_title('Top Ten Influential Taxa', fontsize=18)
    plt.yticks(ind + bar_width/2, y_labels, fontsize=14)
    ax.yaxis.set_tick_params(labelsize=labelsizes)
    ax.xaxis.set_tick_params(labelsize=labelsizes)
    ax.tick_params(axis='x', which='minor', labelsize='0')
    ax.set_xticks(minor_ticks, minor=True)
    
    plt.tight_layout()
    #plt.show()

    full_path = os.path.join(save_path, file_name)
    #pdf=PdfPages(full_path)
    plt.savefig(full_path)
    plt.close()
    #fig.savefig(pdf, format='tiff')
    #pdf.close()
    return y_labels

