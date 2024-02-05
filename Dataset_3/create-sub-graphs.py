# We want to create a function that creates subgraphs of instance graphs
import csv
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import os


def spliter(s,spl,ind):
    indx=[i for i,j in enumerate(s) if j==spl][ind-1]
    return [s[:indx].strip(),s[indx+1:].strip()]


df = pd.read_pickle('PermitLog_SE.pkl')


mapping = pd.read_csv('mapping.csv')

###____MOD_B____###
# Will create "Sub_Instance_graphs" directory if it does not exit
if not os.path.exists("Sub_Instance_graphs"):
    os.makedirs("Sub_Instance_graphs")

event = 0
for prova in df['Status_ALL']:
    list_to_graph = []
    for key in prova.keys():
        graph = mapping.loc[mapping["case:concept:name"] == key]["case_number_id_graphs"].tolist()[0]
        graph_path = f'Instance_graphs/{graph}'

        with open(graph_path, 'r') as file:
            testo = file.readlines()
            #print(testo)
            #print(prova[key])
            inner_list = []
            for i in testo:
                for j in prova[key]:
                    if j in i:
                        if i[0] == 'v':
                            if i not in inner_list:
                                inner_list.append(i)
                        else:
                            vertex = spliter(i, ' ', 3)[1].split('__')
                            vertex.remove(j)
                            if vertex[0] in prova[key]:
                                if i not in inner_list:
                                    inner_list.append(i)
            #inner_list = [x.strip() for x in inner_list]
            #print(inner_list)
            inner_list.insert(0, f'{key}\n')
            inner_list.append('\n')
            list_to_graph = list_to_graph + inner_list
            #print(list_to_graph)
    with open(f'Sub_Instance_graphs/sub_instance_graph_{event}.g', 'w') as f:
        f.writelines(list_to_graph)

    event = event + 1
