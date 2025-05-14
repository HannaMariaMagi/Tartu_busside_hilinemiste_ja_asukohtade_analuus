import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Read the preprocessed data
all_years = pd.read_csv('peatuste_keskmised_hilinemised_2019_2024.csv')

# Get top 3 by year
top3_by_year = (
    all_years
    .sort_values(["year", "arrival_difference_minutes"], ascending=[True, False])
    .groupby("year")
    .head(3)
    .reset_index(drop=True)
)

# Create the visualization
plt.figure(figsize=(14, 8))

# Get unique stop IDs and create a color mapping with distinct colors
unique_ids = sorted(top3_by_year["to_stop_id"].unique())
num_colors_needed = len(unique_ids)

# Create a custom color palette using seaborn's color_palette
colors = sns.color_palette("husl", n_colors=num_colors_needed)
id_to_color = dict(zip(unique_ids, colors))

x_pos = []
x_labels = []
bar_colors = []
y_values = []

bar_index = 0
spacing = 0.7

for year in sorted(top3_by_year["year"].unique()):
    subset = top3_by_year[top3_by_year["year"] == year]
    for j, (_, row) in enumerate(subset.iterrows()):
        x = bar_index + j
        x_pos.append(x)
        y_values.append(row["arrival_difference_minutes"])
        x_labels.append(f"{year}")
        bar_colors.append(id_to_color[row["to_stop_id"]])
    bar_index += len(subset) + spacing

# Create bar plot
bars = plt.bar(x_pos, y_values, color=bar_colors)

# Add labels
for i, bar in enumerate(bars):
    height = bar.get_height()
    stop_name = top3_by_year.iloc[i]["to_stop_name"]
    count = top3_by_year.iloc[i]["count"]
    label = f"{stop_name}\n{height:.1f} min\n(n={count})"
    plt.text(bar.get_x() + bar.get_width()/2, height + 0.1, label,
            ha='center', va='bottom', fontsize=8)

plt.title("Iga aasta top 3 kõige suuremate keskmiste hilinemistega peatust")
plt.ylabel("Keskmine hilinemine (minutites)")
plt.xticks(ticks=x_pos, labels=x_labels, rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.ylim(0, 6)
plt.tight_layout()
plt.savefig("aastate_suurimad_keskmised_hilinejad.png", dpi=300)
plt.show()