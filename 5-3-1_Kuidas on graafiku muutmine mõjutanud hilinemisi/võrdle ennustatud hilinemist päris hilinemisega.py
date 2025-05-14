import pandas as pd
import os

INPUT_FOLDER = "hilinemised_peatuste_vahel"
OUTPUT_FILE = "../daily_summaries.csv"

# Create or overwrite the output CSV
with open(OUTPUT_FILE, "w") as f:
    f.write("year,date,avg_delay_min,median_delay_min,percent_over_3min,num_rows\n")

# Go through each file and summarize
for filename in os.listdir(INPUT_FOLDER):
    if not filename.endswith(".csv failid"):
        continue

    file_path = os.path.join(INPUT_FOLDER, filename)
    try:
        df = pd.read_csv(file_path)

        if 'arrival_difference_seconds' not in df.columns or 'date' not in df.columns:
            continue

        # Compute derived values
        df['delay_minutes'] = df['arrival_difference_seconds'] / 60
        year = pd.to_datetime(df['date'], errors='coerce').dt.year.iloc[0]
        if pd.isnull(year):
            continue

        # Calculate summary stats
        avg_delay = df['delay_minutes'].mean()
        median_delay = df['delay_minutes'].median()
        over_3min = (df['delay_minutes'].abs() > 3).mean() * 100
        num_rows = len(df)

        # Append to CSV
        with open(OUTPUT_FILE, "a") as f:
            f.write(f"{int(year)},{df['date'].iloc[0]},{avg_delay:.2f},{median_delay:.2f},{over_3min:.2f},{num_rows}\n")

        print(f"Processed: {filename}")

    except Exception as e:
        print(f"Failed to process {filename}: {e}")

# After processing all files, print yearly summary
try:
    summary_df = pd.read_csv(OUTPUT_FILE)
    yearly_summary = summary_df.groupby('year').agg({
        'avg_delay_min': 'mean',
        'median_delay_min': 'mean',
        'percent_over_3min': 'mean',
        'num_rows': 'sum'
    }).reset_index()

    print("\nYearly Comparison Table:")
    print(yearly_summary.to_string(index=False))
except Exception as e:
    print(f"Failed to load or summarize daily summaries: {e}")
