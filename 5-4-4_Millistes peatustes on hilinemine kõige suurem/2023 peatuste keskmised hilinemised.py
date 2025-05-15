import pandas as pd
import os
import glob
from datetime import datetime

folder_path = "../hilinemised_peatuste_vahel"
all_files = glob.glob(os.path.join(folder_path, "2023-*.csv"))

all_data = []
for file in sorted(all_files):
    date_str = os.path.basename(file).split('.')[0]  # Gets YYYY-MM-DD
    date = datetime.strptime(date_str, '%Y-%m-%d')

    df = pd.read_csv(file)
    # Convert seconds to minutes
    df['arrival_difference_minutes'] = df['arrival_difference_seconds'] / 60
    df['year'] = date.year
    df['month'] = date.month
    all_data.append(df)

if not all_data:
    raise ValueError("No data files found for 2023!")

# Combine all data
df = pd.concat(all_data, ignore_index=True)

# Group by month and calculate averages
monthly_stats = (df.groupby(['year', 'month', 'to_stop_id', 'to_stop_name'])
                 .agg({
    'arrival_difference_minutes': 'mean',
    'to_stop_id': 'count'
})
                 .rename(columns={'to_stop_id': 'count'})
                 .reset_index())

# Get top 3 by month
top3_by_month = (monthly_stats.sort_values('arrival_difference_minutes', ascending=False)
                 .groupby('month')
                 .head(3)
                 .reset_index(drop=True))

# Save to CSV
top3_by_month.to_csv('2023_peatuste_keskmised_hilinemised_kuude_kaupa.csv', index=False)