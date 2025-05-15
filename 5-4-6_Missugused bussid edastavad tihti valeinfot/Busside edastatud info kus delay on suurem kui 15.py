import pandas as pd
import os
from tqdm import tqdm
import glob

# Input and output paths
input_folder = '../busside_paevased_andmed'
output_file = os.path.join('csv failid', 'big_delays.csv')
chunk_size = 100000
DELAY_THRESHOLD = 15 * 60  # 15 minutes in seconds

# Create output directory if it doesn't exist
os.makedirs(os.path.dirname(output_file), exist_ok=True)

# Get list of .csv files
csv_files = glob.glob(os.path.join(input_folder, '*.csv'))

# Create header in output file
header_written = False

# Process each file with a proper tqdm progress bar
for file_path in tqdm(csv_files, desc="Processing files", unit="file"):
    try:
        chunk_iterator = pd.read_csv(file_path, chunksize=chunk_size, dtype={2: str})
        for chunk in chunk_iterator:
            if 'delay' in chunk.columns:
                high_delay_rows = chunk[abs(chunk['delay']) > DELAY_THRESHOLD]
                if not high_delay_rows.empty:
                    high_delay_rows.to_csv(
                        output_file,
                        mode='a' if header_written else 'w',
                        header=not header_written,
                        index=False
                    )
                    header_written = True
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

print(f"Processing complete. Results saved to {output_file}")
