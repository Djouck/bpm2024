# This script is expected to separate all the instance graphs contained in
# the txt file where all instance graphs are stored (IG_file)
import itertools


def split_list(lst, val):
    return [list(group) for k, group in itertools.groupby(lst, lambda x: x == val) if not k]


# We first need to open the IG_file in reading mode
with open('PrepaidTravelCost_instance_graphs_withPromConformance.g', 'r') as file:
    reader = file.readlines()
    instance_graphs = split_list(reader, 'XP \n')
    print(instance_graphs[0:15])
    i = 1
    for el in instance_graphs:
        single_graph = f'instance_graph_{i}'
        with open(single_graph, 'w') as new_file:
            new_file.writelines(el)
        i = i + 1






