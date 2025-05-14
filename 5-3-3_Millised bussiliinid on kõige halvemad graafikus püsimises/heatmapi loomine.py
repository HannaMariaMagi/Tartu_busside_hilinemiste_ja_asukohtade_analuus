import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from collections import defaultdict, OrderedDict
import csv

# === SISEND: kuupäev, liin, suund ===
kuu = input("Sisesta kuu kujul YYYY-MM (nt 2023-08): ").strip()
route_id = input("Sisesta liini number (nt 12): ").strip()
direction_id = input("Sisesta suund (nt 1): ").strip()

# === Lae peatuste nimed ===
stops_df = pd.read_csv("/data/csv failid/tartu_stops.csv")
stop_name_map = dict(zip(stops_df['stop_code'], stops_df['stop_name']))  # või stop_id

# === Failikaustad ===
busdata_path = "/data/busside_paevased_andmed"
delaydata_path = "/data/hilinemised_peatuste_vahel"

# === Abifunktsioon peatuste järjestuse leidmiseks ===
def extract_stop_order_from_file(filepath, route_id, direction_id):
    stop_seq_map = dict()
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['route_id'] == route_id and row['direction_id'] == direction_id:
                try:
                    seq = int(row['current_stop_sequence'])
                except ValueError:
                    continue
                stop_id = row['stop_id']
                if seq not in stop_seq_map:
                    stop_seq_map[seq] = stop_id
    return [stop_seq_map[k] for k in sorted(stop_seq_map)]

# === Algne väärtused ===
current_order = None
previous_order = None

# Gruppida erinevate liinivariatsioonide heatmapid
variant_index = 1
summary_data_by_variant = []

# Iteratsioon päevade kaupa
for day in range(1, 32):
    date_str = f"{kuu}-{day:02d}"
    bus_file = os.path.join(busdata_path, f"{date_str}.csv")
    delay_file = os.path.join(delaydata_path, f"{date_str}.csv")

    if not os.path.exists(bus_file) or not os.path.exists(delay_file):
        continue

    current_order = extract_stop_order_from_file(bus_file, route_id, direction_id)

    if previous_order and current_order != previous_order:
        # Peatuste järjestus muutus → salvesta eelmised andmed ja alusta uut varianti
        summary_df = (
    pd.DataFrame(summary_data_by_variant)
    .groupby(['hour', 'to_stop_id'])['avg_delay']
    .mean()
    .reset_index()
)
        if not summary_df.empty:
            heatmap_df = summary_df.pivot(index='hour', columns='to_stop_id', values='avg_delay')
            ordered_stops_in_data = [sid for sid in previous_order if sid in heatmap_df.columns]
            heatmap_df = heatmap_df[ordered_stops_in_data]
            heatmap_df.columns = [stop_name_map.get(sid, sid) for sid in heatmap_df.columns]

            plt.figure(figsize=(22, 10))
            sns.heatmap(
                heatmap_df,
                cmap="coolwarm",
                center=0,
                annot=False,
                fmt=".0f",
                linecolor="white",
                linewidths=0.5
            )
            plt.title(f"Keskmine hilinemine (sekundites) liinil {route_id}, suund {direction_id} – {kuu}, variant {variant_index}")
            plt.ylabel("Tund")
            plt.xlabel("Bussipeatus")
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()

            filename = f"heatmap_liin{route_id}_suund{direction_id}_{kuu}_variant{variant_index}.png"
            plt.savefig(filename, dpi=300)
            print(f"Salvestatud: {filename}")
            plt.close()

        # Algata uus variant
        summary_data_by_variant = []
        variant_index += 1

    # Töötle päev hilinemised_peatuste_vahel failist
    df = pd.read_csv(delay_file, usecols=['route_id', 'direction_id', 'to_stop_id', 'arrival_difference_seconds', 'predicted_arrival_time'])
    df = df[(df['route_id'] == int(route_id)) & (df['direction_id'] == int(direction_id))]
    df['hour'] = df['predicted_arrival_time'].apply(lambda x: datetime.strptime(x, "%H:%M:%S").hour)

    grouped = df.groupby(['hour', 'to_stop_id'])['arrival_difference_seconds'].agg(['sum', 'count'])
    for (hour, stop_id), row in grouped.iterrows():
        total = row['sum']
        count = row['count']
        summary_data_by_variant.append({'hour': hour, 'to_stop_id': stop_id, 'avg_delay': total / count})

    previous_order = current_order

# Salvesta viimane variant kui andmeid veel sees
if summary_data_by_variant:
    summary_df = pd.DataFrame(summary_data_by_variant)
    if not summary_df.empty:
        heatmap_df = summary_df.pivot(index='hour', columns='to_stop_id', values='avg_delay')
        ordered_stops_in_data = [sid for sid in previous_order if sid in heatmap_df.columns]
        heatmap_df = heatmap_df[ordered_stops_in_data]
        heatmap_df.columns = [stop_name_map.get(sid, sid) for sid in heatmap_df.columns]

        plt.figure(figsize=(22, 10))
        sns.heatmap(
            heatmap_df,
            cmap="coolwarm",
            center=0,
            annot=False,
            fmt=".0f",
            linecolor="white",
            linewidths=0.5
        )
        plt.title(f"Keskmine hilinemine (sekundites) liinil {route_id}, suund {direction_id} – {kuu}, variant {variant_index}")
        plt.ylabel("Tund")
        plt.xlabel("Bussipeatus")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        filename = f"heatmap_liin{route_id}_suund{direction_id}_{kuu}_variant{variant_index}.png"
        plt.savefig(filename, dpi=300)
        print(f"Salvestatud: {filename}")
        plt.close()
