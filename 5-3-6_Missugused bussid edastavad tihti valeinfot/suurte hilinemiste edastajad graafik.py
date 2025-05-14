import pandas as pd
import matplotlib.pyplot as plt

# Lae CSV andmed
df = pd.read_csv("vehicle_delay_summary_with_labels_minutes.csv")

# Filtreeri välja ainult 'Ridango test'
df = df[df["vehicle_label"] != "Ridango test"]

# Sorteeri 'count' alusel ja võta TOP 10
top10 = df.sort_values(by="count", ascending=False).head(10)

# Joonista graafik
plt.figure(figsize=(12, 6))
bars = plt.bar(top10["vehicle_label"], top10["mean_delay_min"], color='darkblue')
plt.axhline(0, color='gray', linestyle='--')
plt.title("TOP 10 bussi valeinfot edastamise sageduse järgi (sh Live Pos)")
plt.ylabel("Keskmine vale hilinemine (minutites)")
plt.xlabel("Bussi numbrimärk (vehicle_label)")
plt.xticks(rotation=45)
plt.grid(axis="y", linestyle="--", alpha=0.6)

# Lisa n= annotatsioonid
for bar, count in zip(bars, top10["count"]):
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        height + (2 if height > 0 else -6),
        f"n={count}",
        ha='center',
        va='bottom' if height > 0 else 'top',
        fontsize=9
    )

plt.tight_layout()

# Salvesta PNG failina
plt.savefig("top10_suurimate_hilinemistega.png", dpi=300)
plt.show()
