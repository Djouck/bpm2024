import pandas as pd
import pm4py
from datetime import datetime, timedelta
import graphviz
import copy
import gc
import itertools
import os
import csv
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import os


class Event:
    def __init__(self, case, activity, timestamp, rem_time):
        self.case = case
        self.activity = activity
        self.timestamp = timestamp
        self.rem_time = rem_time


def add_second(date_object):
    try:
        in_format_time = datetime.strptime(str(date_object), '%Y-%m-%d %H:%M:%S.%f%z')
    except ValueError:
        in_format_time = datetime.strptime(str(date_object), '%Y-%m-%d %H:%M:%S%z')
    result = in_format_time + timedelta(0, 3)
    return result


def sub_second(date_object):
    try:
        in_format_time = datetime.strptime(str(date_object), '%Y-%m-%d %H:%M:%S.%f%z')
    except ValueError:
        in_format_time = datetime.strptime(str(date_object), '%Y-%m-%d %H:%M:%S%z')
    result = in_format_time - timedelta(0, 3)
    return result


def for_minute(num):
    return num/60


def for_hour(num):
    return num/3600


def for_day(num):
    return num/86400


input_file_path = 'PermitLog_SE_noSpace.xes'
outputname = 'mapping.csv'

# Write to Pandas Dataframe
log = pm4py.read_xes(input_file_path)
df = pm4py.convert_to_dataframe(log)

#df = df[0:10000]

#df = df[0:1000]

# useful for mapping with instance-graphs file
lista_casi = []
a = 1
for i in range(0, len(df)):
    if i == 0:
        lista_casi.append(f'instance_graph_{a}')
    else:
        val_prec = df['case:concept:name'][i-1]
        val = df['case:concept:name'][i]
        if val == val_prec:
            lista_casi.append(f'instance_graph_{a}')
        else:
            a = a + 1
            lista_casi.append(f'instance_graph_{a}')

df['case_number_id_graphs'] = lista_casi

gc.collect()
# to maintain the right order of cases (in particular Start and End activity)
"""
for i in range(0, len(df)):
    if (df['concept:name'] == 'START')[i]:
        df['time:timestamp'][i] = sub_second(df['time:timestamp'][i])
    elif (df['concept:name'] == 'END')[i]:
        df['time:timestamp'][i] = add_second(df['time:timestamp'][i])
    else:
        continue
"""
###____MOD_B____###
"""
for i in range(0, len(df)):
    if df['concept:name'][i] == 'START':
        df.loc[i, 'time:timestamp'] = sub_second(df['time:timestamp'][i])
    elif df['concept:name'][i] == 'END':
        df.loc[i, 'time:timestamp'] = add_second(df['time:timestamp'][i])
    else:
        continue
"""


#df_top = df.head()
#print(df_top)
#print(df['case:Rfp-id'])

# df = pd.read_csv(fname, delimiter=",", header=0)

# create dictionary
dCaTi = {}

# group by "case:concept:name" and compute max timestamp for each group
grouped_df = df.groupby("case:concept:name")["time:timestamp"].max().reset_index()

# convert the timestamp to string and create the dictionary
dCaTi = dict(zip(grouped_df["case:concept:name"], grouped_df["time:timestamp"].astype(str)))

# add a column with remaining time in seconds
help_list = []

for r in df.iterrows():
    try:
        max_time = datetime.strptime(str(dCaTi[r[1]["case:concept:name"]]), '%Y-%m-%d %H:%M:%S.%f%z')
    except ValueError:
        max_time = datetime.strptime(str(dCaTi[r[1]["case:concept:name"]]), '%Y-%m-%d %H:%M:%S%z')
    try:
        actual_time = datetime.strptime(str(r[1]["time:timestamp"]), '%Y-%m-%d %H:%M:%S.%f%z')
    except ValueError:
        actual_time = datetime.strptime(str(r[1]["time:timestamp"]), '%Y-%m-%d %H:%M:%S%z')
    seconds = (max_time-actual_time).total_seconds()
    help_list.append(seconds)

df['remainingTime_sec'] = help_list
# print(df[0:20])
gc.collect()

# add columns with remaining time in minutes, hours, days

df['remainingTime_minutes'] = df["remainingTime_sec"].apply(for_minute)

df['remainingTime_hours'] = df["remainingTime_sec"].apply(for_hour)

df['remainingTime_days'] = df["remainingTime_sec"].apply(for_day)


# order timestamps

# There is a problem here... In ordering different activities with same time...
# And we donot have START e END event...
df['Index'] = df.index
df = df.sort_values(by=['time:timestamp', 'Index'])

# add new column "Status_ALL": for every row in dataframe, a dictionary with every running case as key and
# occurred events per running case as value
df["Status_ALL"] = None

dCaLE = {}  # dictionary of Cases and List of Events occurred
i = 0
inner_list = []

for r in df.iterrows():
    print(i)
    # <class 'tuple'> 24071 Case ID  Case 3608, Activity  START, Complete Timestamp  2010-01-13 08:40:24.999, ...
    cID = r[1]['case:concept:name'].strip()
    act = r[1]['concept:name'].strip()
    date = r[1]['time:timestamp']
    rt = r[1]['remainingTime_sec']

    ev = Event(cID, act, date, rt)

    if cID in dCaLE:
        l = copy.deepcopy(dCaLE[cID])  # .append(ev)
        newL = []
        for item in l:
            newL.append(item)
        newL.append(ev.activity)

        dCaLE[cID] = copy.deepcopy(newL)
    else:
        dCaLE[cID] = copy.deepcopy([ev.activity])
    if ev.activity == 'END':
        del dCaLE[ev.case]

    state = copy.deepcopy(dCaLE)

    inner_list.append(state)

    i += 1



df["Status_ALL"] = inner_list

# mapping creation to map case ID to instance-graph ID
mapping = df[["case:concept:name", "case_number_id_graphs"]].drop_duplicates()

status = df['Status_ALL'].tolist()




# Write to CSV

mapping.to_csv(outputname)

# This script is expected to separate all the instance graphs contained in
# the txt file where all instance graphs are stored (IG_file)



def split_list(lst, val):
    return [list(group) for k, group in itertools.groupby(lst, lambda x: x == val) if not k]

###____MOD_B____###
# Will create "Instance_graphs" directory if it does not exit
if not os.path.exists("Instance_graphs"):
    os.makedirs("Instance_graphs")

# We first need to open the IG_file in reading mode
with open('PermitLog_SE_noSpace.g', 'r') as file:
    reader = file.readlines()
    instance_graphs = split_list(reader, 'XP\n')
    #print(instance_graphs[0:15])
    i = 1
    for el in instance_graphs:
        single_graph = f'Instance_graphs/instance_graph_{i}'
        with open(single_graph, 'w') as new_file:
            new_file.writelines(el)
        i = i + 1

# We want to create a function that creates subgraphs of instance graphs
import csv
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import os


def spliter(s,spl,ind):
    indx=[i for i,j in enumerate(s) if j==spl][ind-1]
    return [s[:indx].strip(),s[indx+1:].strip()]


#df = pd.read_pickle('PermitLog_SE.pkl')


mapping = pd.read_csv('mapping.csv')

###____MOD_B____###
# Will create "Sub_Instance_graphs" directory if it does not exit
if not os.path.exists("Sub_Instance_graphs"):
    os.makedirs("Sub_Instance_graphs")


for index, row in df.iterrows():
    prova = row['Status_ALL']
    list_to_graph = []
    for key in prova.keys():
        graph = mapping.loc[mapping["case:concept:name"] == key]["case_number_id_graphs"].tolist()[0]
        graph_path = f'Instance_graphs/{graph}'

        with open(graph_path, 'r') as file:
            testo = file.readlines()
            # print(testo)
            # print(prova[key])
            inner_list = []
            pluto = 1
            node_list = []
            for i in testo:
                for j in prova[key]:
                    if j in i:
                        if i[0] == 'v':
                            node = int(i.strip().split(' ')[1])
                            if pluto == node:
                                node_list.append(node)
                                if i not in inner_list:
                                    inner_list.append(i)
                                    pluto = pluto + 1
                        else:
                            arc = i.strip().split(' ')[1:3]
                            if int(arc[0]) in node_list:
                                if int(arc[1]) in node_list:
                                    # vertex = i.strip().split(' ')[3].split('__')
                                    # vertex.remove(j)
                                    # if vertex[0] in prova[key]:
                                    if i not in inner_list:
                                        inner_list.append(i)
            # inner_list = [x.strip() for x in inner_list]
            # print(inner_list)
            inner_list.insert(0, f'{key}\n')
            inner_list.append('\n')
            list_to_graph = list_to_graph + inner_list
    with open(f'Sub_Instance_graphs/sub_instance_graph_{index}.g', 'w') as f:
        f.writelines(list_to_graph)
df.to_pickle('PermitLog_SE.pkl')


# Write to CSV

mapping.to_csv(outputname)
