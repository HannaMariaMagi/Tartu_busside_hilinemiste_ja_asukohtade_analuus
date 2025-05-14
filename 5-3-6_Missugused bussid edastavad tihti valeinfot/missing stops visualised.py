import pandas as pd
import os

# Kataloog, kus asuvad failid (muuda vastavalt vajadusele)
data_folder = 'busside_paevased_andmed'
target_stop = '7820336-1'

# Otsi esimest vastet
for filename in os.listdir(data_folder):
    if filename.endswith('.csv failid'):
        file_path = os.path.join(data_folder, filename)
        try:
            df = pd.read_csv(file_path)
            if 'stop_id' in df.columns and 'route_id' in df.columns and 'stop_sequence' in df.columns:
                match = df[df['stop_id'] == target_stop]
                if not match.empty:
                    print(f"Leitud failist: {filename}")
                    print(match[['route_id', 'stop_sequence']].drop_duplicates())
                    break
        except Exception as e:
            print(f"Viga faili {filename} töötlemisel: {e}")
