import csv
import pandas as pd

filename = 'vivaItalia.pkl'
outputname = 'mapping.csv'

df = pd.read_pickle(filename)

#mapping = df[["case:Rfp-id", "case_number_id_graphs"]].drop_duplicates()
#print(mapping)

#for r in df.iterrows():
    #for k,v in df['Status_ALL']:
    #print(r['Status_ALL'])


for i in range(5):
    print(type(df.loc[i]['Status_ALL']))
    print(df.loc[i]['Status_ALL'])

#mapping.to_csv(outputname)
