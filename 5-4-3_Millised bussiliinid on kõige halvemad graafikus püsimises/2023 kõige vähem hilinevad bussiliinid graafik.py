import pandas as pd
import matplotlib.pyplot as plt
import os
import glob
import matplotlib.cm as cm

# Lae ainult 2023 failid
folder_path = "../hilinemised_peatuste_vahel"
all_files = glob.glob(os.path.join(folder_path, "2023-*.csv"))

results = []

for file in all_files:
    try:
        df = pd.read_csv(file, usecols=['route_id', 'direction_id', 'arrival_difference_seconds', 'date'])
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['arrival_difference_seconds'] = pd.to_numeric(df['arrival_difference_seconds'], errors='coerce')
        df['month'] = df['date'].dt.month

        grouped = df.groupby(['month', 'route_id', 'direction_id'])['arrival_difference_seconds'].mean().reset_index()
        results.append(grouped)
    except Exception as e:
        continue  # Vaikne viga, kui fail on katkine või veerud puuduvad

# Ühenda kõik kuud
if results:
    all_months = pd.concat(results)
    monthly_avg = all_months.groupby(['month', 'route_id', 'direction_id'])['arrival_difference_seconds'].mean().reset_index()

    # Top 3 kõige kiiremat liini iga kuu kohta
    top3_by_month = (
        monthly_avg
        .groupby('month', group_keys=False)
        .apply(lambda x: x.nsmallest(3, 'arrival_difference_seconds'))
        .reset_index(drop=True)
    )

    # Kuude nimed
    month_names = {
        1: "Jaanuar", 2: "Veebruar", 3: "Märts", 4: "Aprill",
        5: "Mai", 6: "Juuni", 7: "Juuli", 8: "August",
        9: "September", 10: "Oktoober", 11: "November", 12: "Detsember"
    }

    # --- Graafiku seadistus ---
    plt.figure(figsize=(14, 9))

    # Unikaalsed route_id värvideks
    unique_routes = top3_by_month['route_id'].unique()
    colors = cm.get_cmap('tab20', len(unique_routes))
    route_to_color = {route: colors(i) for i, route in enumerate(unique_routes)}

    x_pos = []
    x_labels = []
    bar_colors = []
    y_values = []

    bar_index = 0
    spacing = 0.40  # vahe iga kuu ploki vahel

    for month in sorted(top3_by_month['month'].unique()):
        subset = top3_by_month[top3_by_month['month'] == month]
        for j, (_, row) in enumerate(subset.iterrows()):
            x = bar_index + j  # ühtlane järjestus kuusiseselt
            x_pos.append(x)
            y_values.append(row['arrival_difference_seconds'])
            x_labels.append(f"{month_names[month]}")
            bar_colors.append(route_to_color[row['route_id']])
        bar_index += len(subset) + spacing  # liigu edasi ainult pärast kuu töötlemist

    # Joonista tulbad
    bars = plt.bar(x_pos, y_values, color=bar_colors)

    # Lisa sildid veergude peale
    for i, bar in enumerate(bars):
        height = bar.get_height()
        route = int(top3_by_month.iloc[i]['route_id'])
        direction = int(top3_by_month.iloc[i]['direction_id'])
        label_text = f"Liin {route}\nSuund {direction}\n{int(height)}s"
        plt.text(bar.get_x() + bar.get_width()/2, height + 1, label_text, ha='center', va='bottom', fontsize=8)

    # Teljed ja kujundus
    plt.title("2023: Iga kuu top 3 hilinenud bussiliini (keskmine hilinemine sekundites)")
    plt.ylabel("Keskmine hilinemine (sekundit)")
    plt.xticks(ticks=x_pos, labels=x_labels, rotation=45)
    plt.ylim(bottom=120)  # Alustame y-telge 100 sekundist
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig("bot3_delays_2023.png", dpi=300)  # ← salvestab PNG faili
    plt.show()
else:
    print("2023. aasta kohta ei leitud ühtegi sobivat CSV-faili või failides puuduvad vajalikud andmed.")
