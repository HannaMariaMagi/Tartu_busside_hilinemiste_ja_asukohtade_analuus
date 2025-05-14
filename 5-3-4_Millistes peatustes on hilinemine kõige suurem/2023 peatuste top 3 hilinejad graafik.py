import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read the existing data
df = pd.read_csv('2023_peatuste_keskmised_hilinemised_kuude_kaupa.csv')

# Get top 1 by month
top1_by_month = (df.sort_values('arrival_difference_minutes', ascending=False)
                 .groupby('month')
                 .head(1)
                 .reset_index(drop=True)
                 .sort_values('month'))  # Sort by month to ensure Jan-Dec order

# Create visualization
plt.figure(figsize=(15, 8))

# Get unique stop IDs and create color mapping
unique_ids = sorted(top1_by_month["to_stop_id"].unique())
colors = plt.colormaps['tab20'](np.linspace(0, 1, len(unique_ids)))
id_to_color = dict(zip(unique_ids, colors))

# Estonian month names
month_names = {
    1: 'Jaanuar', 2: 'Veebruar', 3: 'Märts', 4: 'Aprill',
    5: 'Mai', 6: 'Juuni', 7: 'Juuli', 8: 'August',
    9: 'September', 10: 'Oktoober', 11: 'November', 12: 'Detsember'
}

# Create bar plot
x = range(len(top1_by_month))
bars = plt.bar(x,
               top1_by_month['arrival_difference_minutes'],
               color=[id_to_color[stop_id] for stop_id in top1_by_month['to_stop_id']])

# Add labels
for i, bar in enumerate(bars):
    height = bar.get_height()
    stop_name = top1_by_month.iloc[i]["to_stop_name"]
    count = top1_by_month.iloc[i]["count"]
    label = f"{stop_name}\n{height:.1f} min\n(n={count})"
    plt.text(bar.get_x() + bar.get_width()/2, height + 0.1, label,
            ha='center', va='bottom', fontsize=8)

plt.title("2023. aasta igakuised kõige suurema keskmise hilinemisega peatus", pad=20)
plt.ylabel("Keskmine hilinemine (minutites)")
plt.xticks(x, [month_names[m] for m in top1_by_month['month']], rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.ylim(0, 6)

# Add legend with just stop IDs
legend_elements = [plt.Rectangle((0,0),1,1, facecolor=color)
                  for stop_id, color in id_to_color.items()]
legend_labels = [f"ID: {stop_id}" for stop_id in id_to_color.keys()]
plt.legend(legend_elements, legend_labels,
          title="Peatused",
          loc='upper right',  # Position legend inside the plot
          ncol=2)  # Use 2 columns to make it more compact

plt.tight_layout()
plt.savefig("2023_kuude_suurimad_keskmised_hilinejad.png",
            dpi=300,
            bbox_inches='tight')
plt.show()