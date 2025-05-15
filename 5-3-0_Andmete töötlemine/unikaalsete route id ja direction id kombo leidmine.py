import pandas as pd
import os
from glob import glob
from tqdm import tqdm
from collections import defaultdict

# Kaust, kus andmefailid asuvad
kaust = '../busside_paevased_andmed'  # muuda vastavalt
failid = glob(os.path.join(kaust, '*.csv'))

# Kogume kombinatsioonid ja nende ridade arvu
kombod_loendur = defaultdict(int)

for fail in tqdm(failid, desc='Failide töötlemine'):
    try:
        for chunk in pd.read_csv(
            fail,
            usecols=['route_id', 'direction_id'],
            chunksize=100_000,
            dtype={'route_id': str, 'direction_id': 'Int64'}
        ):
            chunk = chunk.dropna(subset=['route_id', 'direction_id'])
            for row in chunk.itertuples(index=False):
                key = (row.route_id, int(row.direction_id))
                kombod_loendur[key] += 1
    except Exception as e:
        print(f"Viga failis {fail}: {e}")

# Loome DataFrame tulemuste salvestamiseks
df_kogutud = pd.DataFrame(
    [(rid, did, count) for (rid, did), count in kombod_loendur.items()],
    columns=['route_id', 'direction_id', 'ridade_arv']
)

# Sorteeri route_id alusel
df_kogutud = df_kogutud.sort_values(by=['route_id', 'direction_id'])

# Salvesta CSV-failina
df_kogutud.to_csv('route_direction_ridade_arv.csv', index=False)

print(f"Salvestatud {len(df_kogutud)} kombinatsiooni koos ridade arvuga.")
