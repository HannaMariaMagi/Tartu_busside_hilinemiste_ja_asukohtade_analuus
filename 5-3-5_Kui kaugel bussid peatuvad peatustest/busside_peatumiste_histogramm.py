import pandas as pd
import matplotlib.pyplot as plt
import glob
import numpy as np

# Algväärtusta massiiv
distances = []

# Leia mai 2023 failid
mai_failid = glob.glob("/data/bussid_STOPPED_AT_staatusega_2023/2023-05-*.csv")

# Töötle iga fail
for fail in mai_failid:
    chunks = pd.read_csv(fail,
                         usecols=['stop_id', 'distance_from_stop_meters'],
                         chunksize=10000)

    for chunk in chunks:
        chunk['stop_id'] = chunk['stop_id'].astype(str)

        # Filtreeri väärtused, mis on kuni 28 m kaugusel
        valid = chunk[chunk['distance_from_stop_meters'] <= 28]
        distances.extend(valid['distance_from_stop_meters'].values)

        del chunk  # vabasta mälu

# Konverdi numpy massiiviks
distances = np.array(distances)

# Joonista histogramm
plt.figure(figsize=(10, 6))
plt.hist(distances, bins=50, color='skyblue', edgecolor='black')
plt.title("Bussi peatumise kaugus (≤ 28 m) olemasoleva kauguseveeru põhjal - Mai 2023")
plt.xlabel("Kaugus (meetrites)")
plt.ylabel("Peatumiste arv")
plt.grid(True, axis='both', which='major', linestyle='-', alpha=0.2)
plt.grid(True, axis='x', which='minor', linestyle='--', alpha=0.2)
plt.minorticks_on()
plt.xticks(np.arange(0, max(distances)+1, 1))  # Iga 1 m tagant

# Salvesta histogramm
plt.savefig("bussi_peatumise_kaugus_mai_2023.png", dpi=300, bbox_inches='tight')
plt.show()

# Statistika
print(f"Kokku peatumisi: {len(distances)}")
print(f"Keskmine kaugus: {np.mean(distances):.2f} meetrit")
print(f"Mediaan kaugus: {np.median(distances):.2f} meetrit")
