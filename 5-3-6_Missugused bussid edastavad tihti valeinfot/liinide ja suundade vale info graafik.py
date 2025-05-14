import pandas as pd
import matplotlib.pyplot as plt

# Lae andmed
df = pd.read_csv("big_delays.csv")
df["arrival_delay_min"] = df["arrival_delay"] / 60
df = df[df["vehicle_label"] != "Live Pos"]

# Arvuta iga liini ja suuna kohta statistika
route_dir_stats = df.groupby(["route_id", "direction_id"])["arrival_delay_min"].agg(
    count="count",
    mean_delay_min="mean",
    std_delay_min="std"
).reset_index()

# Leia top 5 liini kõige rohkemate valeinfoga ridade põhjal
top_routes = (
    route_dir_stats.groupby("route_id")["count"].sum()
    .sort_values(ascending=False)
    .head(5)
    .index.tolist()
)

# Filtreeri nende liinide suunad
route_dir_stats = route_dir_stats[route_dir_stats["route_id"].isin(top_routes)]

# X-telje silt
route_dir_stats["label"] = route_dir_stats.apply(
    lambda row: f"Liin {row['route_id']} suund {row['direction_id']}", axis=1
)

# Joonista graafik koos ±std
plt.figure(figsize=(12, 6))
bars = plt.bar(
    route_dir_stats["label"],
    route_dir_stats["mean_delay_min"],
    yerr=route_dir_stats["std_delay_min"],
    capsize=5,
    color="darkorange",
    error_kw=dict(ecolor='gray', lw=0.8, alpha=0.6)
)

plt.axhline(0, color='gray', linestyle='--')
plt.title("5 suurimat liini, mis edastavad kõige rohkem valeinfot: keskmine vale saabumisaeg ± standardhälve", fontsize=14)
plt.ylabel("Keskmine vale hilinemine (minutites)")
plt.xlabel("Liin ja suund")
plt.xticks(rotation=45, ha='right')
plt.grid(axis="y", linestyle="--", alpha=0.6)

# Annotatsioonid: n, std, ja keskmine
for bar, count, std, mean in zip(
    bars,
    route_dir_stats["count"],
    route_dir_stats["std_delay_min"],
    route_dir_stats["mean_delay_min"]
):
    height = bar.get_height()
    offset = 8 if height > 0 else -16
    va = 'bottom' if height > 0 else 'top'
    text = f"n={count}\nμ={mean:.1f}\n±{std:.1f}"
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        height + offset,
        text,
        ha='center',
        va=va,
        fontsize=10
    )

plt.tight_layout()
plt.savefig("top5_routes_directions_mean_delay_with_std_highlighted.png", dpi=300)
plt.show()
