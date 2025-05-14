import pandas as pd
import os
import matplotlib.pyplot as plt
from collections import defaultdict

INPUT_FOLDER = "hilinemised_peatuste_vahel"
OUTPUT_IMAGE = "yearly_predicted_delay.png"

# Collect yearly delay statistics without holding full DataFrames in memory
delay_accumulator = defaultdict(lambda: {'actual': [], 'predicted': []})

for filename in os.listdir(INPUT_FOLDER):
    if not filename.endswith(".csv failid"):
        continue

    try:
        df = pd.read_csv(
            os.path.join(INPUT_FOLDER, filename),
            usecols=['arrival_difference_seconds', 'predicted_delay_seconds', 'date']
        )
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
        df['year'] = df['date'].dt.year
        df['delay_minutes'] = df['arrival_difference_seconds'] / 60
        df = df[df['delay_minutes'].abs() <= 15]  # remove outliers

        for year, group in df.groupby('year'):
            delay_accumulator[year]['actual'].extend(group['delay_minutes'].tolist())
            if 'predicted_delay_seconds' in group.columns:
                predicted = group['predicted_delay_seconds'] / 60
                predicted = predicted[predicted.abs() <= 15]
                delay_accumulator[year]['predicted'].extend(predicted.tolist())

    except Exception as e:
        print(f"Skipping {filename}: {e}")

# Calculate yearly averages
summary = pd.DataFrame([
    {
        'year': year,
        'Keskmine hilinemine': round(sum(values['actual']) / len(values['actual']), 2) if values['actual'] else None,
        'Keskmine prognoositud hilinemine': round(sum(values['predicted']) / len(values['predicted']), 2) if values['predicted'] else None
    }
    for year, values in delay_accumulator.items()
])

summary = summary.set_index('year').reindex(range(2019, 2025)).sort_index()

# Plot the results
fig, ax = plt.subplots(figsize=(10, 6))
summary.plot(kind='bar', ax=ax)
ax.set_title("Keskmine busside hilinemine ja ennustus aastate lõikes")
ax.set_xlabel("Aasta")
ax.set_ylabel("Keskmine hilinemine (minutites)")
ax.legend(title="Tüüp")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(OUTPUT_IMAGE)
print(f"✅ Graafik salvestatud kui '{OUTPUT_IMAGE}'")
