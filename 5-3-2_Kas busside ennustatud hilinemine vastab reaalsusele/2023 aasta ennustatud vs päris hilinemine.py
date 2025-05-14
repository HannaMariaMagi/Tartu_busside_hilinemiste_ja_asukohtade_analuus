import pandas as pd
import os
import matplotlib.pyplot as plt
from collections import defaultdict
import numpy as np

INPUT_FOLDER = "../hilinemised_peatuste_vahel"
OUTPUT_IMAGE = "monthly_predicted_delay_with_std_2023.png"

delay_accumulator = defaultdict(lambda: {'actual': [], 'predicted': []})

for filename in os.listdir(INPUT_FOLDER):
    if not filename.endswith(".csv") or not filename.startswith("2023-"):
        continue  # ⛔ Vahele kõik, mis pole 2023

    try:
        df = pd.read_csv(
            os.path.join(INPUT_FOLDER, filename),
            usecols=['arrival_difference_seconds', 'predicted_delay_seconds', 'date']
        )

        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
        df['month'] = df['date'].dt.month

        df['delay_minutes'] = df['arrival_difference_seconds'] / 60
        df = df[(df['delay_minutes'] >= -15) & (df['delay_minutes'] <= 15)]

        for month, group in df.groupby('month'):
            delay_accumulator[month]['actual'].extend(group['delay_minutes'].tolist())

            if 'predicted_delay_seconds' in group.columns:
                predicted = group['predicted_delay_seconds'] / 60
                predicted = predicted[(predicted >= -15) & (predicted <= 15)]
                delay_accumulator[month]['predicted'].extend(predicted.tolist())

    except Exception as e:
        print(f"⚠️ Skipping {filename}: {e}")

# Arvuta kuu keskmised ja standardhälbed
summary = pd.DataFrame([
    {
        'month': month,
        'Keskmine hilinemine': np.mean(values['actual']) if values['actual'] else np.nan,
        'Hilinemise std': np.std(values['actual']) if values['actual'] else np.nan,
        'Keskmine prognoositud hilinemine': np.mean(values['predicted']) if values['predicted'] else np.nan,
        'Prognoosi std': np.std(values['predicted']) if values['predicted'] else np.nan
    }
    for month, values in delay_accumulator.items()
])

summary = summary.set_index('month').reindex(range(1, 13)).sort_index()

# Joonista veerugraafik koos standardhälvetega
fig, ax = plt.subplots(figsize=(12, 6))
bar_width = 0.4
months = summary.index

ax.bar(months - bar_width/2, summary['Keskmine hilinemine'],
       yerr=summary['Hilinemise std'], width=bar_width, label="Tegelik hilinemine", capsize=5)

ax.bar(months + bar_width/2, summary['Keskmine prognoositud hilinemine'],
       yerr=summary['Prognoosi std'], width=bar_width, label="Prognoositud hilinemine", capsize=5)

ax.set_title("Keskmine busside hilinemine ja prognoos koos standardhälvetega (2023)")
ax.set_xlabel("Kuu")
ax.set_ylabel("Hilinemine (minutites)")
ax.set_xticks(range(1, 13))
ax.set_xticklabels(['Jaan', 'Veebr', 'Märts', 'Apr', 'Mai', 'Juun',
                    'Juuli', 'Aug', 'Sept', 'Okt', 'Nov', 'Dets'])
ax.legend()
plt.tight_layout()
plt.savefig(OUTPUT_IMAGE)
print(f"✅ Graafik koos standardhälvetega salvestatud kui '{OUTPUT_IMAGE}'")
