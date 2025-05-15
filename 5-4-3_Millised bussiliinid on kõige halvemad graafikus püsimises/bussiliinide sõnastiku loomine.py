import csv
import json
from collections import defaultdict
from pathlib import Path

# Sisendfail
input_file = Path("/data/busside_paevased_andmed/2023-05-03.csv")

# Väljundkaust
output_dir = Path("/5-4-3_Millised bussiliinid on kõige halvemad graafikus püsimises")
output_dir.mkdir(parents=True, exist_ok=True)

# Väljundfaili nimi sama kuupäevaga
output_file = output_dir / f"stop_order_by_route_and_direction_{input_file.stem}.json"

# Liinistruktuur
stop_order_by_route_and_direction = defaultdict(lambda: defaultdict(dict))

# Loeme CSV mälutõhusalt
with input_file.open("r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        route_id = row['route_id']
        direction_id = row['direction_id']
        try:
            sequence = int(row['current_stop_sequence'])
        except ValueError:
            continue
        stop_id = row['stop_id']

        if sequence not in stop_order_by_route_and_direction[route_id][direction_id]:
            stop_order_by_route_and_direction[route_id][direction_id][sequence] = stop_id

# Muudame peatused järjestatud listideks
for route_id in stop_order_by_route_and_direction:
    for direction_id in stop_order_by_route_and_direction[route_id]:
        sequence_dict = stop_order_by_route_and_direction[route_id][direction_id]
        ordered_stops = [sequence_dict[k] for k in sorted(sequence_dict)]
        stop_order_by_route_and_direction[route_id][direction_id] = ordered_stops

# Teisendame salvestatavaks kujuks
serializable_dict = {
    route_id: dict(directions)
    for route_id, directions in stop_order_by_route_and_direction.items()
}

# Salvestame JSON-faili
with output_file.open("w", encoding="utf-8") as f:
    json.dump(serializable_dict, f, ensure_ascii=False, indent=2)

print(f"Salvestatud: {output_file}")
