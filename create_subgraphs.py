# We want to create a function that creates subgraphs of instance graphs
import csv
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt


df = pd.read_pickle('vivaItalia.pkl')


mapping = pd.read_csv('mapping.csv')
event = 0
for prova in df['Status_ALL']:
    list_to_graph = []
    for key in prova.keys():
        graph = mapping.loc[mapping["case:Rfp-id"] == key]["case_number_id_graphs"].tolist()[0]
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
                            vertex = i.strip().split(' ')[3].split('__')
                            vertex.remove(j)
                            if vertex[0] in prova[key]:
                                if i not in inner_list:
                                    inner_list.append(i)
            #inner_list = [x.strip() for x in inner_list]
            print(inner_list)
            inner_list.insert(0, f'{key}\n')
            inner_list.append('\n')
            list_to_graph = list_to_graph + inner_list
            print(list_to_graph)
    with open(f'sub_instance_graph_{event}.g', 'w') as f:
        f.writelines(list_to_graph)

    event = event + 1
    if event == 500:
        break

