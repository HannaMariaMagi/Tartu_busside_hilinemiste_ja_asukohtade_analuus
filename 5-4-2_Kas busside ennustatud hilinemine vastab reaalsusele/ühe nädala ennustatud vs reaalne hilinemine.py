import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

# Laadi andmed
folder_path = "../hilinemised_peatuste_vahel"
dates_needed = [
    "2023-05-08", "2023-05-09", "2023-05-10",
    "2023-05-11", "2023-05-12", "2023-05-13", "2023-05-14"
]

# Leia ainult valitud failid
target_files = [
    os.path.join(folder_path, f)
    for f in os.listdir(folder_path)
    if any(date in f for date in dates_needed) and f.endswith(".csv")
]

# Laadi ja ühenda
dfs = [pd.read_csv(file) for file in target_files]
df = pd.concat(dfs, ignore_index=True)

# Kombineeri kuupäev ja kellaaeg
df["datetime_actual"] = pd.to_datetime(df["date"] + " " + df["actual_arrival_time"], errors='coerce')
df["datetime_predicted"] = pd.to_datetime(df["date"] + " " + df["predicted_arrival_time"], errors='coerce')
df = df.dropna(subset=["datetime_actual", "datetime_predicted"])

# Ümarda tunnini
df["datetime_hour"] = df["datetime_actual"].dt.floor("H")

# Arvuta hilinemised minutites
df["actual_delay_min"] = (df["datetime_actual"] - df["datetime_predicted"]).dt.total_seconds() / 60
df["predicted_delay_min"] = df["avg_predicted_delay_seconds"] / 60

# Eemalda outlier’id
df = df[(df["actual_delay_min"] >= -10) & (df["actual_delay_min"] <= 60)]

# Gruppimine
hourly_avg = df.groupby("datetime_hour")[["actual_delay_min", "predicted_delay_min"]].mean().reset_index()
hourly_avg["delay_difference"] = hourly_avg["actual_delay_min"] - hourly_avg["predicted_delay_min"]

# 📊 Graafik kahe x-teljega
fig, ax = plt.subplots(figsize=(14, 6))

# Jooned
ax.plot(hourly_avg["datetime_hour"], hourly_avg["actual_delay_min"], label="Tegelik hilinemine", marker='o')
ax.plot(hourly_avg["datetime_hour"], hourly_avg["predicted_delay_min"], label="Prognoositud hilinemine", marker='s')

# Kellaaeg ülemisel teljel
ax.xaxis.set_major_locator(mdates.HourLocator(interval=4))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax.tick_params(axis='x', labelrotation=45)
fig.subplots_adjust(bottom=0.25)

# Kuupäevad alumisel teljel (päeva keskel)
days = sorted({dt.date() for dt in hourly_avg["datetime_hour"]})
date_midpoints = [pd.to_datetime(f"{d} 12:00") for d in days]
date_labels = [d.strftime('%m-%d') for d in days]

secax = ax.secondary_xaxis('bottom', functions=(lambda x: x, lambda x: x))
secax.set_xticks(date_midpoints)
secax.set_xticklabels(date_labels)
secax.tick_params(axis='x', pad=35)

# Piira X-telge, et eemaldada tühjad ääred
ax.set_xlim(hourly_avg["datetime_hour"].min(), hourly_avg["datetime_hour"].max())
secax.set_xlim(hourly_avg["datetime_hour"].min(), hourly_avg["datetime_hour"].max())

# Kujundus
ax.axhline(0, color='gray', linestyle='--', linewidth=0.8)
ax.set_title("Tunnipõhine keskmine hilinemine ja vahe (8.–14. mai 2023)")
ax.set_xlabel("Kuupäev ja kellaaeg", labelpad=25)  # tõstab teljesildi allapoole
ax.tick_params(axis='x', labelrotation=45)
fig.subplots_adjust(bottom=0.35)  # loob ruumi tekstide jaoks
ax.set_ylabel("Hilinemine (minutit)")
ax.legend()
ax.grid(True)
fig.tight_layout()
plt.savefig("ennustatud_vs_tegelik_hilinemine.png", dpi=300, bbox_inches="tight")
plt.show()
