import pandas as pd
import pm4py
from datetime import datetime, timedelta
import graphviz
import copy


class Event:
    def __init__(self, case, activity, timestamp):
        self.case = case
        self.activity = activity
        self.timestamp = timestamp


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


input_file_path = 'PrepaidTravelCost.xes'
#output_file_path = 'PrepaidTravelCost.csv'
outputname = 'mapping.csv'
# fname = output_file_path
# Write to Pandas Dataframe
log = pm4py.read_xes(input_file_path)  # Input Filename
#print(log.columns)
df = pm4py.convert_to_dataframe(log)
print(df)

column_names = []
for col in df.columns:
    column_names.append(col)
print(column_names)

# useful for mapping with instance-graphs file
lista_casi = []
a = 1
for i in range(0, len(df)):
    if i == 0:
        lista_casi.append(f'instance_graph_{a}')
    else:
        val_prec = df['case:Rfp-id'][i-1]
        val = df['case:Rfp-id'][i]
        if val == val_prec:
            lista_casi.append(f'instance_graph_{a}')
        else:
            a = a + 1
            lista_casi.append(f'instance_graph_{a}')

df['case_number_id_graphs'] = lista_casi

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
for i in range(0, len(df)):
    if df['concept:name'][i] == 'START':
        df.loc[i, 'time:timestamp'] = sub_second(df['time:timestamp'][i])
    elif df['concept:name'][i] == 'END':
        df.loc[i, 'time:timestamp'] = add_second(df['time:timestamp'][i])
    else:
        continue



#df_top = df.head()
#print(df_top)
#print(df['case:Rfp-id'])

# df = pd.read_csv(fname, delimiter=",", header=0)

# create dictionary
dCaTi = {}

# compute a list of all the Case ID
listaCaseID = df["case:Rfp-id"].unique()

# insert last element as a string value
for c in listaCaseID:
    dCaTi[c] = str(max(df.loc[df["case:Rfp-id"] == c]["time:timestamp"]))#.split(".")[0]

# add a column with remaining time in seconds
help_list = []

for r in df.iterrows():
    try:
        max_time = datetime.strptime(str(dCaTi[r[1]["case:Rfp-id"]]), '%Y-%m-%d %H:%M:%S.%f%z')
    except ValueError:
        max_time = datetime.strptime(str(dCaTi[r[1]["case:Rfp-id"]]), '%Y-%m-%d %H:%M:%S%z')
    try:
        actual_time = datetime.strptime(str(r[1]["time:timestamp"]), '%Y-%m-%d %H:%M:%S.%f%z')
    except ValueError:
        actual_time = datetime.strptime(str(r[1]["time:timestamp"]), '%Y-%m-%d %H:%M:%S%z')
    seconds = (max_time-actual_time).total_seconds()
    help_list.append(seconds)

df['remainingTime_sec'] = help_list
# print(df[0:20])

# add columns with remaining time in minutes, hours, days

df['remainingTime_minutes'] = [r[1]["remainingTime_sec"]/60 for r in df.iterrows()]
# print(df[0:20])
df['remainingTime_hours'] = [r[1]["remainingTime_sec"]/3600 for r in df.iterrows()]
# print(df[0:20])
df['remainingTime_days'] = [r[1]["remainingTime_sec"]/86400 for r in df.iterrows()]
# df['remainingTime'] = [(max_time - datetime.strptime(str(r[1]["time:timestamp"]), '%Y-%m-%d %H:%M:%S.%f%z')).total_seconds() for r in df.iterrows()]
# print(dCaTi)
# print(df[0:20])

print(df)

# order timestamps

df = df.sort_values(by=['time:timestamp'])

# add new column "Status_ALL": for every row in dataframe, a dictionary with every running case as key and
# occurred events per running case as value
df["Status_ALL"] = None

dCaLE = {}  # dictionary of Cases and List of Events occurred
i = 0
inner_list = []

#for r in df.iterrows():
#    cID = r[1]['case:Rfp-id']
#    act = r[1]['concept:name']
#    date = r[1]['time:timestamp']
#    print(cID)


for r in df.iterrows():
    #print(i)
    # <class 'tuple'> 24071 Case ID  Case 3608, Activity  START, Complete Timestamp  2010-01-13 08:40:24.999, ...
    cID = r[1]['case:Rfp-id'].strip()
    act = r[1]['concept:name'].strip()
    date = r[1]['time:timestamp']

    ev = Event(cID, act, date)

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

#print(type(inner_list[7]))

# print(inner_list[24071])
df["Status_ALL"] = inner_list
#print(inner_list[0] == inner_list[4])
#print(df[0:20])

#for i in range(len(df)):
    #print(type(df.loc[i]['Status_ALL']))
    #print(df.loc[i]['Status_ALL'])

# mapping creation to map case ID to instance-graph ID
mapping = df[["case:Rfp-id", "case_number_id_graphs"]].drop_duplicates()

status = df['Status_ALL'].tolist()
prova = status[23]
#print(prova)
#print(type(prova))

#for key in prova.keys():
    #print(key)

df.to_pickle('vivaItalia.pkl')
#print(df.iterrows())

# Write to CSV
#df.to_csv(output_file_path)
mapping.to_csv(outputname)

# use of pickle to memorize the dataframe and the dictionary
# creation of graph object (with networkx ?) for each row of the column STATUS_all
# share results with Badar
# duplicates activity
