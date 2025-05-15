import pandas as pd
import glob
from collections import defaultdict

# Leia kõik 2023 failid
failid = glob.glob("/data/bussid_STOPPED_AT_staatusega_2023/2023-*.csv")

# Initsialiseeri loendurid
peatuste_summa = defaultdict(float)
peatuste_loendur = defaultdict(int)

# Töötle failid chunkide kaupa
for fail in failid:
    chunks = pd.read_csv(fail, usecols=['stop_id', 'distance_from_stop_meters'], chunksize=10000)
    for chunk in chunks:
        chunk = chunk[chunk['distance_from_stop_meters'] <= 100]  # eemalda ekstreemid
        for _, row in chunk.iterrows():
            stop = str(row['stop_id'])
            peatuste_summa[stop] += row['distance_from_stop_meters']
            peatuste_loendur[stop] += 1

# Arvuta keskmised
keskmised = pd.DataFrame([
    (stop, peatuste_summa[stop] / peatuste_loendur[stop])
    for stop in peatuste_summa
], columns=['stop_id', 'keskmine_kaugus'])

# Salvesta CSV-faili
keskmised.to_csv("keskmised_peatused_2023.csv", index=False)
print("Salvestatud: keskmised_peatused_2023.csv")
