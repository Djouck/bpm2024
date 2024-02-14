# We want to create a function that creates subgraphs of instance graphs
import csv
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import os
import pickle


def spliter(s,spl,ind):
    indx=[i for i,j in enumerate(s) if j==spl][ind-1]
    return [s[:indx].strip(),s[indx+1:].strip()]


def create_sub_graph(diz):
    list_to_graph = []
    for key in diz.keys():
        graph = mapping.loc[mapping["case:concept:name"] == key]["case_number_id_graphs"].tolist()[0]
        graph_path = f'Instance_graphs/{graph}'
        with open(graph_path, 'r') as file:
            testo = file.readlines()
            # print(testo)
            # print(prova[key])
            inner_list = []
            for i in testo:
                for j in diz[key]:
                    if j in i:
                        if i[0] == 'v':
                            if i not in inner_list:
                                inner_list.append(i)
                        else:
                            vertex = spliter(i, ' ', 3)[1].split('__')
                            vertex.remove(j)
                            if vertex[0] in diz[key]:
                                if i not in inner_list:
                                    inner_list.append(i)
            inner_list.insert(0, f'{key}\n')
            inner_list.append('\n')
            list_to_graph = list_to_graph + inner_list
    return list_to_graph


mapping = pd.read_csv('mapping.csv')
print("Il mapping è stato letto")
###____MOD_B____###
# Will create "Sub_Instance_graphs" directory if it does not exit
if not os.path.exists("Sub_Instance_graphs"):
    os.makedirs("Sub_Instance_graphs")
print("La cartella è stata creata")
with open("inner_dict.pickle", "rb") as file:
    inner_dict = pickle.load(file)
print('Il file pickle inner_dict è stato letto')
event = 0
for key in inner_dict.keys():
    print(f"Leggo il sub-dataframe {key}")
    df = pd.read_pickle(f'{key}.pkl')
    print(f"Il sub-dataframe {key} è stato letto")
    for prova in df['Status_ALL']:
        print("Prendo il dizionario da cui estrarre il sotto-grafo")
        print(event)
        print("Applico la funzione create sub graph")
        pippo = create_sub_graph(prova)
        with open(f'Sub_Instance_graphs/sub_instance_graph_{event}.g', 'w') as f:
            f.writelines(pippo)
        print("Il sub-graph è stato creato")
        event = event + 1
