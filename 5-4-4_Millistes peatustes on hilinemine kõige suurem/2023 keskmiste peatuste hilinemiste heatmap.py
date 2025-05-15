import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Lae hilinemised kuude kaupa
df = pd.read_csv("2023_peatuste_keskmised_hilinemised_kuude_kaupa.csv")

# Lae peatusinfo stop_desc saamiseks
stop_info = pd.read_csv("../csv failid/tartu_stops.csv", usecols=["stop_code", "stop_desc"])

# Seome stop_desc juurde
df = df.merge(stop_info, left_on="to_stop_id", right_on="stop_code", how="left")

# Filtreeri välja Lammimõisa, kui seda leidub
df = df[~df["to_stop_name"].str.contains("Lammimõisa", case=False, na=False)]

# Arvuta aasta keskmine hilinemine igale peatus + nimi kombinatsioonile
top20 = (
    df.groupby(["to_stop_id", "to_stop_name", "stop_desc"])["arrival_difference_minutes"]
    .mean()
    .nlargest(20)
    .reset_index()
)

# Loo täissilt kujul: "nimi – kirjeldus (x.x min)"
top20["label"] = top20.apply(
    lambda row: f"{row['to_stop_name']} – {row['stop_desc']} ({row['arrival_difference_minutes']:.1f} min)",
    axis=1
)

# Tee vastendussõnastik: to_stop_id → silt
id_to_label = dict(zip(top20["to_stop_id"], top20["label"]))

# Filtreeri andmed ainult top 20 kohta ja lisa label
df_top = df[df["to_stop_id"].isin(top20["to_stop_id"])].copy()
df_top["label"] = df_top["to_stop_id"].map(id_to_label)

# Pivoteeri heatmapi jaoks
heatmap_data = df_top.pivot_table(
    index="label",
    columns="month",
    values="arrival_difference_minutes"
)

# Sorteeri peatuse read aasta keskmise hilinemise järgi
heatmap_data["keskmine"] = heatmap_data.mean(axis=1)
heatmap_data = heatmap_data.sort_values("keskmine", ascending=False).drop(columns="keskmine")

# Kuude nimed
month_names = {
    1: 'Jaan', 2: 'Veebr', 3: 'Märts', 4: 'Apr', 5: 'Mai', 6: 'Juuni',
    7: 'Juuli', 8: 'Aug', 9: 'Sept', 10: 'Okt', 11: 'Nov', 12: 'Dets'
}
heatmap_data.columns = [month_names.get(m, m) for m in heatmap_data.columns]

# Joonista heatmap
plt.figure(figsize=(14, 10))
sns.heatmap(
    heatmap_data,
    annot=True, fmt=".1f",
    cmap="OrRd",
    linewidths=0.5,
    cbar_kws={'label': 'Keskmine hilinemine (minutites)'}
)

plt.title("2023. aasta top 20 kõige rohkem hilinenud peatust (kuude lõikes, koos kirjeldusega)", pad=20)
plt.ylabel("Peatus – Kirjeldus (keskmine hilinemine)")
plt.xlabel("Kuu")
plt.tight_layout()
plt.savefig("2023_heatmap_top20_peatused_kirjeldustega.png", dpi=300)
plt.show()
