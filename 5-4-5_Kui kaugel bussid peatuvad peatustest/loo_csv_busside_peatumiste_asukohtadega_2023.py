import pandas as pd
import os
from tqdm import tqdm

# Kaust, kus asuvad sisendfailid
input_folder = '../busside_paevased_andmed'

# Väljundkaust CSV-failide jaoks
output_folder = 'bussid_STOPPED_AT_staatusega_2023'
os.makedirs(output_folder, exist_ok=True)

# Failide nimekiri (filtreerime ainult 2023. aasta failid)
files = sorted([f for f in os.listdir(input_folder) if f.endswith('.csv failid') and f.startswith('2023')])

# Käime läbi kõik failid kaustas progress bariga
for filename in tqdm(files, desc="Töötlen 2023. aasta faile"):
    file_path = os.path.join(input_folder, filename)
    try:
        df = pd.read_csv(file_path)
        # Filtreeri ainult STOPPED_AT read
        df_stopped = df[df['status'] == 'STOPPED_AT']
        # Eemalda duplikaadid trip_id, stop_id, vehicle_id alusel
        df_unique = df_stopped.drop_duplicates(subset=['trip_id', 'stop_id', 'vehicle_id'])
        # Salvesta ühe päeva andmed eraldi CSV-failina
        output_path = os.path.join(output_folder, filename)
        df_unique.to_csv(output_path, index=False)
    except Exception as e:
        print(f"Viga failis {filename}: {e}")

print("Kõigi 2023. aasta päevade peatumised on salvestatud CSV-failidena kausta 'bussid_STOPPED_AT_staatusega_2023'.")
