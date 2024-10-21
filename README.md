# For PrepaidTravelCost dataset avaiable here in github

Required input: .xes and .g files

Avviare prima il main.py, poi instance_graphs_separators.py, poi create_sub_graphs.py

- Il main crea il file mapping tra i case ID e gli instance graphs e poi aggiunge all'event log colonne con il remaining time e una colonna per lo status all
- Instance_graph_separator divide gli instance graphs in diversi file
- create_subgraphs prende un elemento della colonna status_ALL e crea un file '.g' con grafi per ogni caso running in quello specifico momento. Per ciascun grafo (del caso running che si sta considerando) ci saranno nodi delle attività svolte fino a quel momento e relativi archi che si possono prendere dal file degli instance graphs

# For RoadFineManagement dataset

Required input: .xes and .g files

- Run first "Road Fine Management Process"/"Pre processing.py": crea il file mapping tra i case ID e gli instance graphs e poi aggiunge all'event log colonne con il remaining time e una colonna per lo status all
- Then run "Road Fine Management Process"/"Instance graph separator.py": divide gli instance graphs in diversi file
- Run "Road Fine Management Process"/"Create sub instance graphs.py": prende un elemento della colonna status_ALL e crea un file '.g' con grafi per ogni caso running in quello specifico momento. Per ciascun grafo (del caso running che si sta considerando) ci saranno nodi delle attività svolte fino a quel momento e relativi archi che si possono prendere dal file degli instance graphs


Dataset_3 is PermitLog_SE_No_Spaces. Run only pre-processing file.
Dataset_4 is RequestForPayment. Run only preprocessing file.

NB Se non si vuole passare dal file pkl, si possono incollare i tre script in ordine in un unico .py file e lanciare solo quello.
