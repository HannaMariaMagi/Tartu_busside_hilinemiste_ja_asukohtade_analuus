import pandas as pd
import os
import matplotlib.pyplot as plt
from collections import defaultdict

# Sisendkaust, kus asuvad failid, ning väljundpildi nimi
INPUT_FOLDER = "hilinemised_peatuste_vahel"
OUTPUT_IMAGE = "Joonised/seasonal_delay_comparison.png"

# Kogume hilinemise statistikat ilma suuri andmetabeleid mällu hoidmata
delay_accumulator = defaultdict(lambda: {
    '01.01–11.06': [],
    '12.06–27.08': [],
    '28.08–31.12': []
})

# Käime kõik failid kaustas läbi
for filename in os.listdir(INPUT_FOLDER):
    if not filename.endswith(".csv"):
        continue

    try:
        # Loeme ainult vajalikud veerud
        df = pd.read_csv(os.path.join(INPUT_FOLDER, filename), usecols=['arrival_difference_seconds', 'date'])
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
        df['year'] = df['date'].dt.year
        df['delay_minutes'] = df['arrival_difference_seconds'] / 60
        df = df[df['delay_minutes'].abs() <= 15]  # eemaldame ekstreemsed väärtused

        # Määrame päevade põhjal perioodi
        df['day_of_year'] = df['date'].dt.dayofyear
        df['period'] = df['day_of_year'].apply(
            lambda d: '01.01–11.06' if d <= 162 else '12.06–27.08' if d <= 239 else '28.08–31.12'
        )

        # Kogume hilinemisandmeid aasta ja perioodi lõikes
        for (year, period), group in df.groupby(['year', 'period']):
            delay_accumulator[year][period].extend(group['delay_minutes'].tolist())

    except Exception as e:
        print(f"Fail vahele jäetud: {filename} — {e}")

# Arvutame iga aasta kohta keskmised hilinemised
summary = pd.DataFrame([
    {
        'year': year,
        '01.01–11.06': round(sum(values['01.01–11.06']) / len(values['01.01–11.06']), 2) if values['01.01–11.06'] else None,
        '12.06–27.08 (suvegraafik)': round(sum(values['12.06–27.08']) / len(values['12.06–27.08']), 2) if values['12.06–27.08'] else None,
        '28.08–31.12': round(sum(values['28.08–31.12']) / len(values['28.08–31.12']), 2) if values['28.08–31.12'] else None
    }
    for year, values in delay_accumulator.items()
])

summary = summary.set_index('year').sort_index()

# Joonistame tulemused graafikule
fig, ax = plt.subplots(figsize=(10, 6))
summary.plot(kind='bar', ax=ax)
ax.set_title("Keskmine busside hilinemine aastate lõikes")
ax.set_xlabel("Aasta")
ax.set_ylabel("Keskmine hilinemine (minutites)")
ax.legend(title="Periood")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(OUTPUT_IMAGE)
print(f"✅ Graafik salvestatud kui '{OUTPUT_IMAGE}'")
