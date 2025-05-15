import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import glob

# Lae ainult 2023 failid
folder_path = "../hilinemised_peatuste_vahel"
all_files = glob.glob(os.path.join(folder_path, "2023-*.csv"))

results = []

for file in all_files:
    try:
        df = pd.read_csv(file, usecols=['route_id', 'arrival_difference_seconds', 'date'])
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['arrival_difference_seconds'] = pd.to_numeric(df['arrival_difference_seconds'], errors='coerce')
        df['month'] = df['date'].dt.month

        grouped = df.groupby(['month', 'route_id'])['arrival_difference_seconds'].mean().reset_index()
        results.append(grouped)
    except Exception:
        continue  # ignore if file is broken or missing columns

# Ühenda kõik kuud
if results:
    all_months = pd.concat(results)

    # Arvuta kogu aasta peale iga liini kohta keskmine hilinemine
    yearly_avg = all_months.groupby('route_id')['arrival_difference_seconds'].mean().reset_index()

    # Vali 20 kõige rohkem hilinevat liini
    top20_routes = yearly_avg.nlargest(20, 'arrival_difference_seconds')['route_id']

    # Filtreeri need liinid kuude lõikes
    filtered = all_months[all_months['route_id'].isin(top20_routes)]

    # Pivoteeri heatmapi jaoks (liinid vs kuud)
    heatmap_data = filtered.pivot_table(
        index='route_id',
        columns='month',
        values='arrival_difference_seconds'
    )

    # Kuude nimed
    month_names = {
        1: "Jaan", 2: "Veebr", 3: "Märts", 4: "Apr", 5: "Mai", 6: "Juuni",
        7: "Juuli", 8: "Aug", 9: "Sept", 10: "Okt", 11: "Nov", 12: "Dets"
    }
    heatmap_data.columns = [month_names.get(m, m) for m in heatmap_data.columns]
    # Sorteeri ridade järgi (keskmise hilinemise alusel)
    heatmap_data['keskmine'] = heatmap_data.mean(axis=1)
    heatmap_data = heatmap_data.sort_values('keskmine', ascending=False).drop(columns='keskmine')

    # Joonista heatmap
    plt.figure(figsize=(12, 10))
    sns.heatmap(
        heatmap_data,
        annot=True, fmt=".0f",
        cmap="Reds",
        linewidths=.5,
        cbar_kws={'label': 'Keskmine hilinemine (sekundit)'}
    )
    plt.title("Top 20 kõige rohkem hilinevat bussiliini (2023, sorteeritud kogu aasta keskmise järgi)")
    plt.ylabel("Bussiliin (route_id)")
    plt.xlabel("Kuu")
    plt.tight_layout()
    plt.savefig("heatmap_top20_sorted_2023.png", dpi=300)
    plt.show()
else:
    print("2023. aasta kohta ei leitud ühtegi sobivat CSV-faili või failides puuduvad vajalikud andmed.")
