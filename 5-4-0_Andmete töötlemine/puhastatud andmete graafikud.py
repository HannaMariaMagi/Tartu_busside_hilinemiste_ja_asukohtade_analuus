import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates

# --- Lisa graafikumuutuste jooned ja suveperioodid ---
def lisa_jooned(ax):
    muudatused = [
        "2019-09-01", "2020-01-01", "2020-09-01", "2021-01-01",
        "2021-09-01", "2022-01-01", "2022-09-01", "2023-01-01",
        "2023-09-01", "2024-01-01", "2024-09-01"
    ]
    for kuupäev_str in muudatused:
        kuupäev = pd.to_datetime(kuupäev_str)
        ax.axvline(kuupäev, color='red', linestyle='--', linewidth=1)

    ymin, ymax = ax.get_ylim()
    ytext = ymin + (ymax - ymin) * 0.05

    for aasta in range(2020, 2024):  # Suvi 2024 eemaldatud
        suvi_algus = pd.to_datetime(f"{aasta}-06-12")
        suvi_lõpp = pd.to_datetime(f"{aasta}-08-27")
        ax.axvspan(suvi_algus, suvi_lõpp, color='blue', alpha=0.15)
        ax.text(suvi_algus, ytext, f"Suvi {aasta}", color='blue',
                fontsize=7, rotation=90, ha='left', va='bottom')

# --- Abi: kuude kaupa summeerimine ---
def valmistu(df, kuupaevaveerg, veerud_summa):
    df[kuupaevaveerg] = pd.to_datetime(df[kuupaevaveerg], errors='coerce')
    df['kuu'] = df[kuupaevaveerg].dt.to_period('M').dt.to_timestamp()
    df_grouped = df.groupby('kuu')[veerud_summa].sum().reset_index()
    return df_grouped

# --- Kuu nimed eesti keeles ---
kuud_eesti = ['jaan', 'veebr', 'märts', 'apr', 'mai', 'juuni',
              'juuli', 'aug', 'sept', 'okt', 'nov', 'dets']
def kuunimi(dt):
    return kuud_eesti[dt.month - 1]

# --- 1. Ridade arv kuude lõikes ---
df_rows = pd.read_csv('ridade_arv_peale_puhastust.csv')
df_rows_grouped = valmistu(df_rows, 'kuupäev', ['ridade_arv_peale_puhastust'])
df_rows_grouped = df_rows_grouped[df_rows_grouped['kuu'] < '2024-07-01']

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(df_rows_grouped['kuu'], df_rows_grouped['ridade_arv_peale_puhastust'], marker='o')
lisa_jooned(ax)
ax.set_xlim(df_rows_grouped['kuu'].min(), df_rows_grouped['kuu'].max())
ax.yaxis.set_major_formatter(mticker.StrMethodFormatter('{x:,.0f}'))
ax.set_xticks(df_rows_grouped['kuu'])
ax.set_xticklabels([kuunimi(d) for d in df_rows_grouped['kuu']])
ax_secondary = ax.twiny()
ax_secondary.set_xlim(df_rows_grouped['kuu'].min(), df_rows_grouped['kuu'].max())
ax_secondary.set_xticks([d for i, d in enumerate(df_rows_grouped['kuu']) if d.month == 1])
ax_secondary.set_xticklabels([str(d.year) for d in df_rows_grouped['kuu'] if d.month == 1])
ax_secondary.tick_params(axis='x', pad=5, labelsize=9)
ax.tick_params(axis='x', rotation=45, labelsize=9)
ax.set_title('Puhastatud ridade koguarv kuude lõikes')
ax.set_xlabel('')
ax.set_ylabel('Ridade arv')
plt.tight_layout()
plt.savefig('graafik_ridade_arv_kuude_kaupa.png')
plt.close()

# --- 2. Unikaalsed route_id kuude lõikes ---
df_routes = pd.read_csv('unikaalsed_route_id.csv')
df_routes_grouped = valmistu(df_routes, 'kuupäev', ['unikaalseid_route_id'])
df_routes_grouped = df_routes_grouped[df_routes_grouped['kuu'] < '2024-07-01']

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(df_routes_grouped['kuu'], df_routes_grouped['unikaalseid_route_id'], marker='o')
lisa_jooned(ax)
ax.set_xlim(df_rows_grouped['kuu'].min(), df_rows_grouped['kuu'].max())
ax.yaxis.set_major_formatter(mticker.StrMethodFormatter('{x:,.0f}'))
ax.set_xticks(df_routes_grouped['kuu'])
ax.set_xticklabels([kuunimi(d) for d in df_rows_grouped['kuu']])
ax_secondary = ax.twiny()
ax_secondary.set_xlim(ax.get_xlim())
ax_secondary.set_xticks([d for i, d in enumerate(df_rows_grouped['kuu']) if d.month == 1])
ax_secondary.set_xticklabels([str(d.year) for d in df_rows_grouped['kuu'] if d.month == 1])
ax_secondary.tick_params(axis='x', pad=5, labelsize=9)
ax.tick_params(axis='x', rotation=45, labelsize=9)
ax.set_title('Unikaalsete route_id koguarv kuude lõikes')
ax.set_xlabel('')
ax.set_ylabel('Route_id arv')
plt.tight_layout()
plt.savefig('graafik_route_id_kuude_kaupa.png')
plt.close()

# --- 3. Unikaalsed vehicle_id ja ridade arv kuude lõikes ---
df_vehicles = pd.read_csv('unikaalsed_vehicle_id.csv')
df_vehicles_grouped = valmistu(df_vehicles, 'kuupäev', ['unikaalseid_vehicle_id', 'kokku_ridu'])
df_vehicles_grouped = df_vehicles_grouped[df_vehicles_grouped['kuu'] < '2024-07-01']

# a) vehicle_id
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(df_vehicles_grouped['kuu'], df_vehicles_grouped['unikaalseid_vehicle_id'], marker='o')
lisa_jooned(ax)
ax.set_xlim(df_rows_grouped['kuu'].min(), df_rows_grouped['kuu'].max())
ax.yaxis.set_major_formatter(mticker.StrMethodFormatter('{x:,.0f}'))
ax.set_xticks(df_vehicles_grouped['kuu'])
ax.set_xticklabels([kuunimi(d) for d in df_rows_grouped['kuu']])
ax_secondary = ax.twiny()
ax_secondary.set_xlim(ax.get_xlim())
ax_secondary.set_xticks([d for i, d in enumerate(df_rows_grouped['kuu']) if d.month == 1])
ax_secondary.set_xticklabels([str(d.year) for d in df_rows_grouped['kuu'] if d.month == 1])
ax_secondary.tick_params(axis='x', pad=5, labelsize=9)
ax.tick_params(axis='x', rotation=45, labelsize=9)
ax.set_title('Unikaalsete vehicle_id koguarv kuude lõikes')
ax.set_xlabel('')
ax.set_ylabel('Vehicle_id arv')
plt.tight_layout()
plt.savefig('graafik_vehicle_id_kuude_kaupa.png')
plt.close()

# b) kokku ridu
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(df_vehicles_grouped['kuu'], df_vehicles_grouped['kokku_ridu'], marker='o')
lisa_jooned(ax)
ax.set_xlim(df_rows_grouped['kuu'].min(), df_rows_grouped['kuu'].max())
ax.yaxis.set_major_formatter(mticker.StrMethodFormatter('{x:,.0f}'))
ax.set_xticks(df_vehicles_grouped['kuu'])
ax.set_xticklabels([kuunimi(d) for d in df_rows_grouped['kuu']])
ax_secondary = ax.twiny()
ax_secondary.set_xlim(ax.get_xlim())
ax_secondary.set_xticks([d for i, d in enumerate(df_rows_grouped['kuu']) if d.month == 1])
ax_secondary.set_xticklabels([str(d.year) for d in df_rows_grouped['kuu'] if d.month == 1])
ax_secondary.tick_params(axis='x', pad=5, labelsize=9)
ax.tick_params(axis='x', rotation=45, labelsize=9)
ax.set_title('Kokku ridu (vehicle_id failist) kuude lõikes')
ax.set_xlabel('')
ax.set_ylabel('Ridade arv')
plt.tight_layout()
plt.savefig('graafik_vehicle_id_ridu_kuude_kaupa.png')
plt.close()
