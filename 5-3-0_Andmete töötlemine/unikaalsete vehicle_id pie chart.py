import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

# Lae andmed
df = pd.read_csv('route_direction_ridade_arv.csv')
# Muuda route_id stringiks
df['route_id'] = df['route_id'].astype(str)

# Veendu, et ridade arv oleks arvuline
df['ridade_arv'] = pd.to_numeric(df['ridade_arv'], errors='coerce')
df = df.dropna(subset=['ridade_arv'])  # eemalda vigased

# Summeeri route_id tasemel
df_grouped = df.groupby("route_id", as_index=False)["ridade_arv"].sum()

# Kogu summa
total = df_grouped["ridade_arv"].sum()
df_grouped["osakaal"] = df_grouped["ridade_arv"] / total

# Debug print
print("\nBefore threshold filtering:")
print(df_grouped.sort_values('ridade_arv', ascending=False))

# Määrame "Muu" alla väiksemad kui 2%
threshold = 0.02
df_suured = df_grouped[df_grouped["osakaal"] >= threshold].copy()
df_muu = df_grouped[df_grouped["osakaal"] < threshold].copy()

# Debug print
print("\nAfter threshold filtering (df_suured):")
print(df_suured.sort_values('ridade_arv', ascending=False))

# Explicitly sort before adding "Muu"
df_suured = df_suured.sort_values("ridade_arv", ascending=False).reset_index(drop=True)

muu_ridu = df_muu["ridade_arv"].sum()
muu_row = pd.DataFrame({
    "route_id": ["Muu"],
    "ridade_arv": [muu_ridu],
    "osakaal": [muu_ridu / total]
})
df_suured = pd.concat([df_suured, muu_row], ignore_index=True)

# Debug print
print("\nFinal data for visualization:")
print(df_suured)

# Simpler color generation
colors = plt.cm.tab20(np.linspace(0, 1, len(df_suured)))

# Increase figure size and create plot
fig, ax = plt.subplots(figsize=(12, 8))

# Create pie chart
patches, texts, pcts = ax.pie(
    df_suured["ridade_arv"],
    labels=df_suured["route_id"],
    autopct="%.1f%%",
    colors=colors,
    wedgeprops={'linewidth': 2.5, 'edgecolor': 'white'},
    textprops={'fontsize': 10},
    startangle=90,
    radius=0.8,
    pctdistance=0.75
)

# Make percentage labels white and bold
plt.setp(pcts, color='white', fontweight='bold')

# Make the text labels match their wedge colors
for text, patch in zip(texts, patches):
    text.set_color(patch.get_facecolor())
    text.set_fontweight('bold')  # Optional: make labels bold

# Create legend with normal colored text
legend = ax.legend(
    patches,
    [f"Liin {rid}" if rid != "Muu" else rid for rid in df_suured["route_id"]],
    title="Bussiliinid",
    loc="center left",
    bbox_to_anchor=(1.1, 0.5),
    fontsize=10
)

plt.title("Bussiliinide esinemiste osakaal andmetes", fontsize=16, pad=2)
plt.tight_layout(pad=1.5)

# Save and show
plt.savefig("bussiliinide_osakaal.png", bbox_inches='tight', dpi=300)
plt.show()