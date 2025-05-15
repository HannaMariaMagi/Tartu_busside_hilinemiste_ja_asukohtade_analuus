import pandas as pd
import os
import matplotlib.pyplot as plt
from collections import defaultdict

# Sisendkaust, kus asuvad failid, ning väljundpildi nimi
INPUT_FOLDER = "../hilinemised_peatuste_vahel"
OUTPUT_IMAGE = "percent_over_3min.png"

# Kogume statistikat: mitu protsenti hilines >3 minuti
delay_accumulator = defaultdict(lambda: {
    '01.01–11.06': {'over_3_min': 0, 'total': 0},
    '12.06–27.08': {'over_3_min': 0, 'total': 0},
    '28.08–31.12': {'over_3_min': 0, 'total': 0}
})

for filename in os.listdir(INPUT_FOLDER):
    if not filename.endswith(".csv"):
        continue

    try:
        df = pd.read_csv(os.path.join(INPUT_FOLDER, filename), usecols=['arrival_difference_seconds', 'date'])
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
        df['year'] = df['date'].dt.year
        df = df[df['arrival_difference_seconds'] <= 900]  # eemaldame ekstreemsed väärtused

        # Määrame perioodi
        df['day_of_year'] = df['date'].dt.dayofyear
        df['period'] = df['day_of_year'].apply(
        lambda d: '01.01–11.06' if d <= 162 else '12.06–27.08' if d <= 239 else '28.08–31.12'
        )

        for (year, period), group in df.groupby(['year', 'period']):
            total = len(group)
            over_3 = (group['arrival_difference_seconds'] > 180).sum()
            delay_accumulator[year][period]['over_3_min'] += over_3
            delay_accumulator[year][period]['total'] += total

    except Exception as e:
        print(f"Vahele jäetud: {filename} — {e}")

# Arvutame protsendid
summary = pd.DataFrame([
    {
        'year': year,
        '01.01–11.06': round((values['01.01–11.06']['over_3_min'] / values['01.01–11.06']['total']) * 100, 2)
                      if values['01.01–11.06']['total'] > 0 else None,
        '12.06–27.08 (Suvegraafik)': round((values['12.06–27.08']['over_3_min'] / values['12.06–27.08']['total']) * 100, 2)
                      if values['12.06–27.08']['total'] > 0 else None,
        '28.08–31.12': round((values['28.08–31.12']['over_3_min'] / values['28.08–31.12']['total']) * 100, 2)
                      if values['28.08–31.12']['total'] > 0 else None
    }
    for year, values in delay_accumulator.items()
])

summary = summary.set_index('year').sort_index()

# Joonista graafik
fig, ax = plt.subplots(figsize=(10, 6))
summary.plot(kind='bar', ax=ax)
ax.set_title("Hilinemised üle 3 minuti (%) aastate ja perioodide lõikes")
ax.set_xlabel("Aasta")
ax.set_ylabel("Hilinemiste osakaal (%)")
ax.legend(title="Periood")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(OUTPUT_IMAGE)
print(f"✅ Graafik salvestatud kui '{OUTPUT_IMAGE}'")
