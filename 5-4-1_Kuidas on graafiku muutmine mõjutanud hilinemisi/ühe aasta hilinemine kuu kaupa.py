import pandas as pd
import os
import matplotlib.pyplot as plt
from collections import defaultdict

INPUT_FOLDER = "../hilinemised_peatuste_vahel"
OUTPUT_IMAGE = "monthly_delay_2023.png"

monthly_totals = defaultdict(float)
monthly_counts = defaultdict(int)

for filename in os.listdir(INPUT_FOLDER):
    if not filename.endswith(".csv") or not filename.startswith("2023-"):
        continue

    try:
        for chunk in pd.read_csv(
            os.path.join(INPUT_FOLDER, filename),
            usecols=['arrival_difference_seconds', 'date'],
            chunksize=100_000
        ):
            chunk['date'] = pd.to_datetime(chunk['date'], errors='coerce')
            chunk = chunk.dropna(subset=['date'])

            chunk['month'] = chunk['date'].dt.month
            chunk['delay_minutes'] = chunk['arrival_difference_seconds'] / 60
            chunk = chunk[chunk['delay_minutes'].abs() <= 15]

            for month, sub in chunk.groupby('month'):
                monthly_totals[month] += sub['delay_minutes'].sum()
                monthly_counts[month] += sub['delay_minutes'].count()

    except Exception as e:
        print(f"⚠️ Fail vahele jäetud: {filename} — {e}")

# Valmistame andmed jooniseks
summary = pd.DataFrame({
    'month': sorted(monthly_totals.keys()),
    'avg_delay': [round(monthly_totals[m] / monthly_counts[m], 2) for m in sorted(monthly_totals.keys())]
})

# Joonista veergdiagramm
fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(summary['month'], summary['avg_delay'])
ax.set_title("Keskmine busside hilinemine kuude lõikes (2023)")
ax.set_xlabel("Kuu")
ax.set_ylabel("Keskmine hilinemine (minutites)")
ax.set_xticks(range(1, 13))
ax.set_xticklabels(['Jaan', 'Veebr', 'Märts', 'Apr', 'Mai', 'Juun', 'Juuli', 'Aug', 'Sept', 'Okt', 'Nov', 'Dets'])
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig(OUTPUT_IMAGE)
print(f"✅ Graafik salvestatud: {OUTPUT_IMAGE}")
