import pandas as pd
import matplotlib.pyplot as plt

# --- Graafikumuutuste ja suveperioodide tähistamine ---
def lisa_jooned(ax):
    # Punased graafikumuutuste jooned
    muudatused = {
        "Sügisgraafik 2019": "2019-09-01",
        "Talvegraafik 2020": "2020-01-01",
        "Sügisgraafik 2020": "2020-09-01",
        "Talvegraafik 2021": "2021-01-01",
        "Sügisgraafik 2021": "2021-09-01",
        "Talvegraafik 2022": "2022-01-01",
        "Sügisgraafik 2022": "2022-09-01",
        "Talvegraafik 2023": "2023-01-01",
        "Sügisgraafik 2023": "2023-09-01",
        "Talvegraafik 2024": "2024-01-01",
        "Sügisgraafik 2024": "2024-09-01"
    }

    for nimi, kuupäev_str in muudatused.items():
        kuupäev = pd.to_datetime(kuupäev_str)
        ax.axvline(kuupäev, color='red', linestyle='--', linewidth=1)
        ax.text(kuupäev, ax.get_ylim()[1]*0.95, nimi, color='red',
                fontsize=7, rotation=90, ha='right')

    # Sinised varjutused iga-aastase suvegraafiku jaoks
    for aasta in range(2020, 2025):
        suvi_algus = pd.to_datetime(f"{aasta}-06-12")
        suvi_lõpp = pd.to_datetime(f"{aasta}-08-27")
        ax.axvspan(suvi_algus, suvi_lõpp, color='blue', alpha=0.15)
        ax.text(suvi_algus, ax.get_ylim()[1]*0.9, f"Suvi {aasta}", color='blue', fontsize=7)


# --- 1. Puhastatud ridade arv kuude lõikes ---
df_rows = pd.read_csv('ridade_arv_peale_puhastust.csv')
df_rows['kuupäev'] = pd.to_datetime(df_rows['kuupäev'], errors='coerce')
df_rows['kuu'] = df_rows['kuupäev'].dt.to_period('M').dt.to_timestamp()
df_rows_grouped = df_rows.groupby('kuu')['ridade_arv_peale_puhastust'].sum().reset_index()

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(df_rows_grouped['kuu'], df_rows_grouped['ridade_arv_peale_puhastust'], marker='o')
lisa_jooned(ax)
ax.set_title('Puhastatud ridade koguarv kuude lõikes')
ax.set_xlabel('Kuu')
ax.set_ylabel('Ridade arv')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('graafik_ridade_arv_kuude_kaupa.png')
plt.close()


# --- 2. Unikaalsed route_id kokku kuude lõikes ---
df_routes = pd.read_csv('unikaalsed_route_id.csv')
df_routes['kuupäev'] = pd.to_datetime(df_routes['kuupäev'], errors='coerce')
df_routes['kuu'] = df_routes['kuupäev'].dt.to_period('M').dt.to_timestamp()
df_routes_grouped = df_routes.groupby('kuu')['unikaalseid_route_id'].sum().reset_index()

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(df_routes_grouped['kuu'], df_routes_grouped['unikaalseid_route_id'], marker='o')
lisa_jooned(ax)
ax.set_title('Unikaalsete route_id koguarv kuude lõikes')
ax.set_xlabel('Kuu')
ax.set_ylabel('Route_id arv')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('graafik_route_id_kuude_kaupa.png')
plt.close()


# --- 3. Unikaalsed vehicle_id kokku kuude lõikes ---
df_vehicles = pd.read_csv('unikaalsed_vehicle_id.csv')
df_vehicles['kuupäev'] = pd.to_datetime(df_vehicles['kuupäev'], errors='coerce')
df_vehicles['kuu'] = df_vehicles['kuupäev'].dt.to_period('M').dt.to_timestamp()
df_vehicles_grouped = df_vehicles.groupby('kuu')[['unikaalseid_vehicle_id', 'kokku_ridu']].sum().reset_index()

# a) unikaalsed vehicle_id
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(df_vehicles_grouped['kuu'], df_vehicles_grouped['unikaalseid_vehicle_id'], marker='o')
lisa_jooned(ax)
ax.set_title('Unikaalsete vehicle_id koguarv kuude lõikes')
ax.set_xlabel('Kuu')
ax.set_ylabel('Vehicle_id arv')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('graafik_vehicle_id_kuude_kaupa.png')
plt.close()

# b) kokku ridu (vehicle_id failist)
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(df_vehicles_grouped['kuu'], df_vehicles_grouped['kokku_ridu'], marker='o')
lisa_jooned(ax)
ax.set_title('Kokku ridu vehicle_id failist kuude lõikes')
ax.set_xlabel('Kuu')
ax.set_ylabel('Ridade arv')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('graafik_vehicle_id_ridu_kuude_kaupa.png')
plt.close()
