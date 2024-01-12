Avviare prima il main.py, poi instance_graphs_separators.py, poi create_sub_graphs.py

Il main crea il file mapping tra i case ID e gli instance graphs e poi aggiunge all'event log colonne con il remaining time e una colonna per lo status all
Instance_graph_separator divide gli instance graphs in diversi file
create subgraphs prende un elemento della colonna status_ALL e crea un file '.g' con grafi per ogni caso running in quello specifico momento. Per ciascun grafo (del caso running che si sta considerando) ci saranno nodi delle attività svolte fino a quel momento e relativi archi che si possono prendere dal file degli instance graphs
