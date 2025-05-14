import pandas as pd
import glob
import csv

# Parameetrid
stop_id_target = '7801387-1'
output_file = "peatumise_koordinaadid_7801387-1.csv"

# Loo tühi fail koos päisega
with open(output_file, mode='w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['latitude', 'longitude'])

# Läbi kõik 2023 failid
failid = glob.glob("/data/bussid_STOPPED_AT_staatusega_2023/2023*.csv")

for fail in failid:
    chunks = pd.read_csv(fail, usecols=['stop_id', 'latitude', 'longitude'], chunksize=10000)
    for chunk in chunks:
        chunk['stop_id'] = chunk['stop_id'].astype(str)
        matches = chunk[chunk['stop_id'] == stop_id_target][['latitude', 'longitude']]
        matches.to_csv(output_file, mode='a', header=False, index=False)
