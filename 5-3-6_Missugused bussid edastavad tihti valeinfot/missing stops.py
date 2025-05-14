import pandas as pd
import os
from glob import glob
from tqdm import tqdm

# Lae teadaolevad Tartu peatuste stop_code'id
tartu_stops = pd.read_csv("../csv failid/tartu_stops.csv", usecols=["stop_code"])
known_stops = set(tartu_stops['stop_code'].astype(str))

# Tee failide kataloogist
data_dir = "../busside_paevased_andmed"
csv_files = glob(os.path.join(data_dir, "*.csv failid"))

# Tulemuste hoidmiseks
seen = set()
results = []

# Läbi kõik failid progressiribaga
for file_path in tqdm(csv_files, desc="Töötlen faile"):
    try:
        df = pd.read_csv(
            file_path,
            dtype={'stop_id': str},
            usecols=["stop_id", "status", "longitude", "latitude"],
            low_memory=False
        )

        # Filtreeri ridadele, kus stop_id on tundmatu ja staatuseks STOPPED_AT
        filtered = df[(~df['stop_id'].isin(known_stops)) & (df['status'] == "STOPPED_AT")]

        # Võta ainult uued stop_id-d
        filtered = filtered[~filtered['stop_id'].isin(seen)]

        # Lisa uued tulemused ja uuenda nähtud stop_id-de hulka
        for sid, group in filtered.groupby("stop_id"):
            first = group.iloc[0]
            results.append((sid, first['longitude'], first['latitude']))
            seen.add(sid)

    except Exception as e:
        print(f"Viga failis {file_path}: {e}")

# Salvesta CSV-sse
result_df = pd.DataFrame(results, columns=['stop_id', 'longitude', 'latitude'])
result_df.to_csv("missing_stops_with_coords.csv failid", index=False)
