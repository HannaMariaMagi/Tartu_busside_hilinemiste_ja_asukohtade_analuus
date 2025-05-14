import pandas as pd
import os
from collections import defaultdict
from datetime import datetime

INPUT_FOLDER = "busside_paevased_andmed"
OUTPUT_FOLDER = "hilinemised_peatuste_vahel"
LOOKUP_FILE = "../csv failid/tartu_stops.csv"

# Load stop name lookup
stop_lookup_df = pd.read_csv(LOOKUP_FILE)
stop_id_to_name = dict(zip(stop_lookup_df['stop_code'], stop_lookup_df['stop_name']))

# Ensure output folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Process each file in the input folder
for filename in os.listdir(INPUT_FOLDER):
    if not filename.endswith(".csv failid"):
        continue

    filepath = os.path.join(INPUT_FOLDER, filename)
    df = pd.read_csv(filepath, dtype={'route_id': str})

    # Extract date from filename
    date_str = os.path.splitext(filename)[0]
    df['date'] = date_str

    # Build stop order dictionary using vectorized operations
    route_stop_seq_df = df.drop_duplicates(subset=['route_id', 'direction_id', 'current_stop_sequence'])
    stop_order_by_route_and_direction = defaultdict(lambda: defaultdict(list))
    for (rid, did), group in route_stop_seq_df.groupby(['route_id', 'direction_id']):
        ordered = group.sort_values('current_stop_sequence')['stop_id'].tolist()
        stop_order_by_route_and_direction[rid][did] = ordered

    # Analyze each trip_id and vehicle_id
    result_rows = []
    for (trip_id, vehicle_id), group in df.groupby(['trip_id', 'vehicle_id']):
        group = group.sort_values('vehicle_timestamp')
        rid = group['route_id'].iloc[0]
        did = group['direction_id'].iloc[0]
        route_stops = stop_order_by_route_and_direction[rid][did]

        # Precompute average delay for each stop_id in this group
        avg_delay_by_stop = group.groupby('stop_id')['arrival_delay'].mean().round().astype(int).to_dict()

        stop_records = {}
        for row in group.itertuples(index=False):
            sid = row.stop_id
            status = getattr(row, 'status', '')
            ts = row.vehicle_timestamp
            atime = row.arrival_time
            adelay = row.arrival_delay

            if sid not in stop_records:
                stop_records[sid] = {
                    'predicted_arrival_time': atime - adelay,
                    'predicted_delay_seconds': adelay,
                    'STOPPED_AT': None,
                    'INCOMING_AT': None,
                    'IN_TRANSIT_TO': None
                }

            if status in stop_records[sid] and stop_records[sid][status] is None:
                stop_records[sid][status] = ts

        for i in range(1, len(route_stops)):
            from_stop = route_stops[i - 1]
            to_stop = route_stops[i]

            if to_stop in stop_records and from_stop in stop_records:
                pred_time = stop_records[to_stop]['predicted_arrival_time']
                pred_delay = stop_records[to_stop]['predicted_delay_seconds']
                actual_ts = (
                    stop_records[to_stop]['STOPPED_AT'] or
                    stop_records[to_stop]['INCOMING_AT'] or
                    stop_records[to_stop]['IN_TRANSIT_TO']
                )

                if actual_ts is not None:
                    pred_dt = pd.to_datetime(pred_time, unit='s', utc=True).tz_convert('Europe/Tallinn')
                    actual_dt = pd.to_datetime(actual_ts, unit='s', utc=True).tz_convert('Europe/Tallinn')
                    diff_sec = int((actual_dt - pred_dt).total_seconds())

                    if abs(diff_sec) <= 900:
                        avg_delay = avg_delay_by_stop.get(to_stop, pred_delay)

                        result_rows.append({
                            'trip_id': trip_id,
                            'vehicle_id': vehicle_id,
                            'route_id': rid,
                            'direction_id': did,
                            'from_stop_id': from_stop,
                            'from_stop_name': stop_id_to_name.get(from_stop, ''),
                            'to_stop_id': to_stop,
                            'to_stop_name': stop_id_to_name.get(to_stop, ''),
                            'predicted_arrival_time': pred_dt.time(),
                            'predicted_delay_seconds': pred_delay,
                            'avg_predicted_delay_seconds': avg_delay,
                            'actual_arrival_time': actual_dt.time(),
                            'arrival_difference_seconds': diff_sec,
                            'date': date_str
                        })

    # Save result file
    if result_rows:
        result_df = pd.DataFrame(result_rows)
        output_path = os.path.join(OUTPUT_FOLDER, f"{date_str}.csv failid")
        result_df.to_csv(output_path, index=False)
        print(f"Processed and saved: {filename}")
