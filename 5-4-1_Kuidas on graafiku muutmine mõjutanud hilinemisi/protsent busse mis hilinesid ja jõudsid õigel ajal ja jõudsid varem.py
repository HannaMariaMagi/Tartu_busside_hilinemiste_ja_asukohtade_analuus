import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict

# Kaust ja väljundpilt
INPUT_FOLDER = "../hilinemised_peatuste_vahel"
OUTPUT_IMAGE = "percent_grouped_by_period.png"

# Andmekogum: iga aasta ja perioodi kohta kategooriad
delay_accumulator = defaultdict(lambda: {
    '01.01–11.06': {'over_3_min': 0, 'on_time': 0, 'early': 0, 'total': 0},
    '12.06–27.08': {'over_3_min': 0, 'on_time': 0, 'early': 0, 'total': 0},
    '28.08–31.12': {'over_3_min': 0, 'on_time': 0, 'early': 0, 'total': 0}
})

# Töötle faile ükshaaval
for filename in os.listdir(INPUT_FOLDER):
    if not filename.endswith(".csv"):
        continue

    try:
        df = pd.read_csv(os.path.join(INPUT_FOLDER, filename), usecols=['arrival_difference_seconds', 'date'])
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
        df['year'] = df['date'].dt.year

        # Filtreeri ekstreemumid välja
        df = df[(df['arrival_difference_seconds'] >= -900) & (df['arrival_difference_seconds'] <= 900)]

        # Arvuta päev aastas ja jaga perioodideks
        df['day_of_year'] = df['date'].dt.dayofyear
        df['period'] = df['day_of_year'].apply(
            lambda d: '01.01–11.06' if d <= 162 else '12.06–27.08' if d <= 239 else '28.08–31.12'
        )

        # Arvuta iga aasta ja perioodi kohta kategooriad
        for (year, period), group in df.groupby(['year', 'period']):
            total = len(group)
            over_3 = (group['arrival_difference_seconds'] > 180).sum()
            on_time = group['arrival_difference_seconds'].between(-180, 180).sum()
            early = (group['arrival_difference_seconds'] < -180).sum()
            delay_accumulator[year][period]['over_3_min'] += over_3
            delay_accumulator[year][period]['on_time'] += on_time
            delay_accumulator[year][period]['early'] += early
            delay_accumulator[year][period]['total'] += total

    except Exception as e:
        print(f"Vahele jäetud: {filename} — {e}")

# Tabel visualiseerimiseks
data = []
for year, periods in delay_accumulator.items():
    for period, values in periods.items():
        total = values['total']
        if total == 0:
            continue
        combined_label = f"{year} / {period}"
        data.append({'Aasta | Periood': combined_label, 'Tüüp': 'Varajased (< -3min)', 'Protsent': values['early'] / total * 100})
        data.append({'Aasta | Periood': combined_label, 'Tüüp': 'Õigeaegsed (-3min kuni +3min)', 'Protsent': values['on_time'] / total * 100})
        data.append({'Aasta | Periood': combined_label, 'Tüüp': 'Hilinejad (> 3min)', 'Protsent': values['over_3_min'] / total * 100})

summary_df = pd.DataFrame(data)

# Joonista tulpdiagramm
sns.set(style="whitegrid")
plt.figure(figsize=(16, 8))
ax = sns.barplot(
    data=summary_df,
    x="Aasta | Periood",
    y="Protsent",
    hue="Tüüp",
    errorbar=None,
    palette="Set1"
)
ax.set_title("Busside saabumise täpsus aastate ja perioodide lõikes")
ax.set_xlabel("Aasta | Periood")
ax.set_ylabel("Osakaal (%)")
plt.xticks(rotation=45, ha="right")
plt.legend(title="Saabumise kategooria")
plt.tight_layout()
plt.savefig(OUTPUT_IMAGE)
print(f"✅ Graafik salvestatud kui '{OUTPUT_IMAGE}'")
