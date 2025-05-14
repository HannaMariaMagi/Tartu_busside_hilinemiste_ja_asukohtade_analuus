import os
import json
import csv
import zstandard as zstd
import shutil

# Väljundkaust CSV-failide jaoks
output_folder = "/andmed/busside_paevased_andmed"
os.makedirs(output_folder, exist_ok=True)

# Kaust, kuhu töödeldud .zst failid liigutatakse
processed_folder = "/andmed/toodeldud_zst_failid"
os.makedirs(processed_folder, exist_ok=True)

def extract_entities(json_obj):
    rows = []
    for entity in json_obj.get("entities", []):
        trip = entity.get("tripUpdate", {}).get("trip", {})
        vehicle = entity.get("vehicle", {})
        vehicle_info = vehicle.get("vehicle", {})
        position = vehicle.get("position", {})
        current_status = vehicle.get("currentStatus", None)
        stop_time_update = next(iter(entity.get("tripUpdate", {}).get("stopTimeUpdates", [])), None)

        if stop_time_update:
            arrival = stop_time_update.get("arrival", {})
            departure = stop_time_update.get("departure", {})
            row = {
                "start_date": trip.get("startDate"),
                "trip_id": trip.get("tripId"),
                "route_id": trip.get("routeId"),
                "direction_id": trip.get("directionId"),
                "start_time": trip.get("startTime"),
                "vehicle_id": vehicle_info.get("id"),
                "vehicle_label": vehicle_info.get("label"),
                "current_stop_sequence": vehicle.get("currentStopSequence"),
                "vehicle_timestamp": vehicle.get("timestamp"),
                "status": current_status,
                "latitude": position.get("latitude"),
                "longitude": position.get("longitude"),
                "bearing": position.get("bearing"),
                "speed": position.get("speed"),
                "stop_id": stop_time_update.get("stopId"),
                "stop_sequence": stop_time_update.get("stopSequence"),
                "arrival_delay": arrival.get("delay"),
                "arrival_time": arrival.get("time"),
                "departure_delay": departure.get("delay"),
                "departure_time": departure.get("time"),
            }
            rows.append(row)
    return rows

def write_rows_to_csv(rows):
    for row in rows:
        date = row['start_date']
        if not date:
            continue

        output_file = os.path.join(output_folder, f"{date}.csv")
        file_exists = os.path.isfile(output_file)

        try:
            with open(output_file, 'a', newline='', encoding='utf-8') as f_out:
                writer = csv.DictWriter(f_out, fieldnames=row.keys())
                if not file_exists:
                    writer.writeheader()
                writer.writerow(row)
        except Exception as e:
            print(f"Failed to write row: {e}")

def process_zst_file(filepath):
    try:
        with open(filepath, 'rb') as f:
            dctx = zstd.ZstdDecompressor()
            with dctx.stream_reader(f) as reader:
                buffer = b""

                while True:
                    chunk = reader.read(65536)
                    if not chunk:
                        break
                    buffer += chunk

                    while b"\n" in buffer:
                        line, buffer = buffer.split(b"\n", 1)
                        if line.strip():
                            try:
                                obj = json.loads(line)
                                rows = extract_entities(obj)
                                if rows:
                                    write_rows_to_csv(rows)
                            except Exception as e:
                                print(f"Line processing error in {os.path.basename(filepath)}: {e}")

        shutil.move(filepath, os.path.join(processed_folder, os.path.basename(filepath)))
        print(f"Moved processed file: {os.path.basename(filepath)}")

    except Exception as e:
        print(f"Error processing {os.path.basename(filepath)}: {e}")

def read_zst_and_split_by_date(folder_path):
    if not os.path.exists(folder_path):
        print(f"Input folder does not exist: {folder_path}")
        return

    for root, dirs, files in os.walk(folder_path):
        zst_files = [os.path.join(root, f) for f in files if f.endswith('.zst')]
        for file in zst_files:
            print(f"Processing: {os.path.basename(file)}")
            process_zst_file(file)

    print("All files processed.")

if __name__ == "__main__":
    read_zst_and_split_by_date("/andmed/zst_bussiinfo")
