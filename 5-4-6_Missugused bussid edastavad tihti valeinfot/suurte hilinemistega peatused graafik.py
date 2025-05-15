import pandas as pd
import matplotlib.pyplot as plt

# Lae andmed
df = pd.read_csv("big_delays.csv")
stops = pd.read_csv("../csv failid/tartu_stops.csv")

# Filter out "Live Pos"
df = df[df["vehicle_label"] != "Live Pos"]

# Convert delay to minutes
df["arrival_delay_min"] = df["arrival_delay"] / 60

# Group by stop_id, compute summary statistics
stop_summary = df.groupby("stop_id")["arrival_delay_min"].agg(
    count="count",
    mean_delay_min="mean",
    std_delay_min="std"
).sort_values(by="count", ascending=False).head(10).reset_index()

# Prepare for merging names and descriptions
stops["stop_code"] = stops["stop_code"].astype(str)
stop_summary["stop_id"] = stop_summary["stop_id"].astype(str)

# Merge stop_name and stop_desc to stop_summary
stop_summary = stop_summary.merge(
    stops[["stop_code", "stop_name", "stop_desc"]],
    left_on="stop_id",
    right_on="stop_code",
    how="left"
)

# Create label: stop name – stop_desc (stop_id)
stop_summary["label"] = stop_summary.apply(
    lambda row: (
        f"{row['stop_name']}\n{row['stop_desc']}\n({row['stop_id']})"
        if pd.notnull(row["stop_desc"])
        else f"{row['stop_name']}\n({row['stop_id']})"
    ),
    axis=1
)

# Plot with larger figure and tighter spacing
plt.figure(figsize=(14, 8))
bars = plt.bar(stop_summary["label"], stop_summary["mean_delay_min"], color="firebrick")
plt.axhline(0, color='gray', linestyle='--')
plt.title("10 peatust, millel on kõige rohkem valesid aegu (va Live Pos)", fontsize=14)
plt.xlabel("Peatus (nimi + kirjeldus + ID)", fontsize=12)
plt.ylabel("Keskmine vale hilinemine (minutites)", fontsize=12)
plt.xticks(rotation=25, ha='right', fontsize=11)
plt.yticks(fontsize=10)
plt.grid(axis="y", linestyle="--", alpha=0.6)

# Add n and std annotations above or below bars
for bar, count, std in zip(bars, stop_summary["count"], stop_summary["std_delay_min"]):
    height = bar.get_height()
    offset = 4 if height > 0 else -6
    alignment = 'bottom' if height > 0 else 'top'
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        height + offset,
        f"n={count}\n±{std:.1f}",
        ha='center',
        va=alignment,
        fontsize=9
    )

plt.ylim(-100, 300)
plt.tight_layout(pad=3.0)
plt.subplots_adjust(bottom=0.3, top=0.9)
plt.savefig("top10_stops_delay_with_ids_and_desc.png", dpi=300)
plt.show()
