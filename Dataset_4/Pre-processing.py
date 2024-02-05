import pandas as pd
import pm4py
from datetime import datetime, timedelta
import graphviz
import copy
import gc


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


input_file_path = 'RequestForPayment.xes'
outputname = 'mapping.csv'

# Write to Pandas Dataframe
log = pm4py.read_xes(input_file_path)
df = pm4py.convert_to_dataframe(log)

#df = df[0:10000]

df = df[0:1000]

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

df.to_pickle('RequestForPayment.pkl')


# Write to CSV

mapping.to_csv(outputname)