import pandas as pd
import os
import glob
from tqdm import tqdm

folder_path = "../hilinemised_peatuste_vahel"
all_files = glob.glob(os.path.join(folder_path, "2023-*.csv"))  # ainult 2023

# Initialize an empty list to store results
monthly_results = []

# Process each file
for file in tqdm(all_files, desc="Töötlen 2023 faile"):
    try:
        # Extract month from filename (eeldusel et failinimi on nt 2023-01-14.csv)
        filename = os.path.basename(file)
        month = int(filename[5:7])

        # Process in chunks
        chunk_size = 100_000
        chunks = pd.read_csv(file,
                             usecols=["to_stop_id", "to_stop_name", "arrival_difference_seconds"],
                             chunksize=chunk_size)

        chunk_results = []

        for chunk in chunks:
            chunk["arrival_difference_seconds"] = pd.to_numeric(chunk["arrival_difference_seconds"], errors="coerce")
            chunk = chunk.dropna(subset=["arrival_difference_seconds"])

            agg = (chunk.groupby("to_stop_id")
                   .agg({
                       "arrival_difference_seconds": ["sum", "count"],
                       "to_stop_name": "first"
                   }))
            chunk_results.append(agg)

        if chunk_results:
            file_result = pd.concat(chunk_results)
            file_result = (file_result.groupby(level=0)
                           .agg({
                               ("arrival_difference_seconds", "sum"): "sum",
                               ("arrival_difference_seconds", "count"): "sum",
                               ("to_stop_name", "first"): "first"
                           }))

            file_result["mean_seconds"] = file_result[("arrival_difference_seconds", "sum")] / file_result[("arrival_difference_seconds", "count")]
            file_result["arrival_difference_minutes"] = file_result["mean_seconds"] / 60
            file_result["month"] = month

            file_result = file_result.reset_index()
            file_result.columns = ["to_stop_id", "sum_seconds", "count", "to_stop_name", "mean_seconds", "arrival_difference_minutes", "month"]

            monthly_results.append(file_result)

    except Exception as e:
        print(f"Viga failis {file}: {e}")
        continue

# Salvestame lõpptulemuse
if monthly_results:
    final_df = pd.concat(monthly_results, ignore_index=True)
    final_df = final_df[["to_stop_id", "to_stop_name", "month", "arrival_difference_minutes"]]
    final_df.sort_values(["month", "arrival_difference_minutes"], ascending=[True, False], inplace=True)

    output_file = "2023_peatuste_keskmised_hilinemised_kuude_kaupa.csv"
    final_df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"\nSalvestatud: {output_file}")
else:
    print("Andmeid ei leitud või viga töötlemisel.")
