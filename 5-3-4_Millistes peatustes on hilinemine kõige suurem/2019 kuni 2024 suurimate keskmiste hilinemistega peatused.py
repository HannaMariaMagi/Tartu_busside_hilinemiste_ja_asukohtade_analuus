import pandas as pd
import matplotlib.pyplot as plt
import os
import glob
import matplotlib.cm as cm
from tqdm import tqdm

folder_path = "../hilinemised_peatuste_vahel"
all_files = glob.glob(os.path.join(folder_path, "*.csv"))

# Initialize an empty DataFrame to store aggregated results
aggregated_results = []
name_mapping = []

# Process each file separately
for file in tqdm(all_files, desc="Töötlen faile"):
    try:
        year = int(os.path.basename(file)[:4])
        
        # Read and process the file in chunks
        chunk_size = 100000  # Adjust this value based on your available memory
        chunks = pd.read_csv(file, 
                           usecols=["to_stop_id", "to_stop_name", "arrival_difference_seconds"],
                           chunksize=chunk_size)
        
        # Process each chunk
        chunk_results = []
        for chunk in chunks:
            chunk["arrival_difference_seconds"] = pd.to_numeric(chunk["arrival_difference_seconds"], 
                                                             errors="coerce")
            
            # Aggregate at chunk level
            chunk_agg = (chunk.groupby("to_stop_id")
                        .agg({
                            "arrival_difference_seconds": ["sum", "count"],
                            "to_stop_name": "first"
                        }))
            chunk_results.append(chunk_agg)
        
        # Combine chunks for this file
        if chunk_results:
            file_result = pd.concat(chunk_results)
            file_result = (file_result.groupby(level=0)
                         .agg({
                             ("arrival_difference_seconds", "sum"): "sum",
                             ("arrival_difference_seconds", "count"): "sum",
                             ("to_stop_name", "first"): "first"
                         }))
            
            # Calculate mean
            file_result["mean_seconds"] = (file_result[("arrival_difference_seconds", "sum")] / 
                                         file_result[("arrival_difference_seconds", "count")])
            file_result["year"] = year
            
            # Convert to more manageable format
            file_result = file_result.reset_index()
            file_result.columns = ["to_stop_id", "sum_seconds", "count", "to_stop_name", 
                                 "mean_seconds", "year"]

            aggregated_results.append(file_result)
            
            # Store name mapping
            name_mapping.append(chunk[["to_stop_id", "to_stop_name"]].drop_duplicates())
            
    except Exception as e:
        print(f"Error processing {file}: {str(e)}")
        continue

if aggregated_results:
    # Combine all results
    all_years = pd.concat(aggregated_results, ignore_index=True)

    # First aggregate by year and stop_id to eliminate duplicates
    all_years = (all_years.groupby(["year", "to_stop_id"])
                 .agg({
        "sum_seconds": "sum",
        "count": "sum",
        "to_stop_name": "first"
    })
                 .reset_index())

    # Recalculate the mean
    all_years["mean_seconds"] = all_years["sum_seconds"] / all_years["count"]

    # Convert to minutes
    all_years["arrival_difference_minutes"] = all_years["mean_seconds"] / 60

    # After calculating all_years but before getting top3_by_year, add:
    output_filename = "peatuste_keskmised_hilinemised_2019_2024.csv"
    all_years.sort_values(["year", "arrival_difference_minutes"], ascending=[True, False], inplace=True)
    all_years.to_csv(output_filename, index=False, encoding='utf-8')

    print(f"\nSaved all stops' yearly average delays to {output_filename}")
    # Get top 3 by year
    top3_by_year = (
        all_years
        .sort_values(["year", "arrival_difference_minutes"], ascending=[True, False])
        .groupby("year")
        .head(3)
        .reset_index(drop=True)
    )

else:
    print("Sobivaid faile ei leitud või andmed puudusid.")