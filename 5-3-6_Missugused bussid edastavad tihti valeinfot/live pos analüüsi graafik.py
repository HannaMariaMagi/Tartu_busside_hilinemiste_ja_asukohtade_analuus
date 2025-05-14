import pandas as pd
import matplotlib.pyplot as plt

# Lae andmed
df = pd.read_csv("big_delays.csv")
stops = pd.read_csv("../csv failid/tartu_stops.csv")

# Arvuta hilinemine minutites
df["arrival_delay_min"] = df["arrival_delay"] / 60

# Filtreeri ainult Live Pos
live_pos_data = df[df["vehicle_label"] == "Live Pos"]

# Groupime stop_id ja route_id järgi
live_pos_grouped = live_pos_data.groupby(["stop_id", "route_id"]).size().reset_index(name="count")

# Võta TOP 10
top_live_pos = live_pos_grouped.sort_values(by="count", ascending=False).head(10)

# Lisa peatuse nimi ja kirjeldus (sobitame stop_code vastu)
stops["stop_code"] = stops["stop_code"].astype(str)
top_live_pos["stop_id"] = top_live_pos["stop_id"].astype(str)

top_live_pos = top_live_pos.merge(
    stops[["stop_code", "stop_name", "stop_desc"]],
    left_on="stop_id",
    right_on="stop_code",
    how="left"
)

# Koosta X-telje silt: "Nimi – Kirjeldus (stop_id, Liin X)"
top_live_pos["label"] = top_live_pos.apply(
    lambda row: (
        f"{row['stop_name']} – {row['stop_desc']}\n({row['stop_id']}, Liin {row['route_id']})"
        if pd.notnull(row["stop_desc"])
        else f"{row['stop_name']} ({row['stop_id']}, Liin {row['route_id']})"
    ),
    axis=1
)

# Joonista graafik
plt.figure(figsize=(12, 6))
bars = plt.bar(top_live_pos["label"], top_live_pos["count"], color="teal")
plt.title("TOP 10 Live Pos kombinatsiooni: Peatus + Liin (sh kirjeldus)")
plt.xlabel("Peatus (ID + liin)")
plt.ylabel("Valeinfot sisaldavate teadete arv (n)")
plt.grid(axis="y", linestyle="--", alpha=0.6)

# Lisa annotatsioonid
for bar, count in zip(bars, top_live_pos["count"]):
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        height + 100,
        f"n={count}",
        ha='center',
        va='bottom',
        fontsize=9
    )

plt.tight_layout()
plt.savefig("livepos_stops_routes_with_names.png", dpi=300)
plt.show()
