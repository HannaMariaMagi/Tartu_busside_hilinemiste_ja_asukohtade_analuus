import pandas as pd
import numpy as np
import glob
import os
from math import radians, sin, cos, sqrt, atan2

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371000  # Maa raadius meetrites
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c

# Lae peatuste andmed (ainult vajalikud veerud)
peatused = pd.read_csv("/data/csv failid/tartu_stops.csv", 
                       usecols=['stop_code', 'stop_lat', 'stop_lon'])
peatused['stop_code'] = peatused['stop_code'].astype(str)

# Leia kõik failid kaustas
failid = glob.glob("/data/bussid_STOPPED_AT_staatusega_2023/*.csv")

# Töötle iga fail
for fail in failid:
    print(f"Töötlen faili: {fail}")
    
    # Loe fail tükkidena
    chunk_size = 10000
    chunks = pd.read_csv(fail, chunksize=chunk_size)
    
    # Loo väljundfaili nimi
    väljundfail = fail.replace('.csv', '_with_distance.csv')
    
    # Kirjuta päis väljundfaili
    first_chunk = True
    
    for chunk in chunks:
        # Konverdi stop_id stringiks
        chunk['stop_id'] = chunk['stop_id'].astype(str)
        
        # Ühenda peatuste andmetega
        merged = chunk.merge(peatused, 
                           left_on='stop_id', 
                           right_on='stop_code', 
                           how='left')
        
        # Arvuta kaugus
        merged['distance_from_stop_meters'] = merged.apply(
            lambda row: haversine_distance(
                row['latitude'], row['longitude'],
                row['stop_lat'], row['stop_lon']
            ),
            axis=1
        )
        
        # Vali ainult originaalsed veerud + uus kauguse veerg
        result = chunk.copy()
        result['distance_from_stop_meters'] = merged['distance_from_stop_meters']
        
        # Kirjuta tulemus faili
        if first_chunk:
            result.to_csv(väljundfail, index=False)
            first_chunk = False
        else:
            result.to_csv(väljundfail, mode='a', header=False, index=False)
        
        # Vabasta mälu
        del merged
        del result
    
    print(f"Valmis: {väljundfail}")
    
    # Kui kõik on õnnestunud, asenda vana fail uuega
    os.replace(väljundfail, fail)

print("Kõik failid on töödeldud!")