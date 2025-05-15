import pandas as pd
import folium

# Failid
punktid_csv = "peatumise_koordinaadid_7801387-1.csv"
stops_csv = "/data/csv failid/tartu_stops.csv"

# Lae punktid
punktid = pd.read_csv(punktid_csv)

# Lae peatuse ametlik asukoht
stops = pd.read_csv(stops_csv, usecols=['stop_code', 'stop_lat', 'stop_lon'])
peatus = stops[stops['stop_code'] == '7801387-1'].iloc[0]
peatus_lat = peatus['stop_lat']
peatus_lon = peatus['stop_lon']

# Kaardi keskpunkt: ametlik peatus
kaart = folium.Map(location=[peatus_lat, peatus_lon], zoom_start=16)

# Lisa punktid kaardile
for _, row in punktid.iterrows():
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=2,
        color='blue',
        fill=True,
        fill_opacity=0.5
    ).add_to(kaart)

# Lisa ametlik peatusepunkt
folium.Marker(
    location=[peatus_lat, peatus_lon],
    popup="Ametlik peatus",
    icon=folium.Icon(color='red', icon='bus', prefix='fa')
).add_to(kaart)

# Salvesta kaardifail
kaart.save("peatus_7801387-1_kaart.html")
print("Kaart salvestatud: peatus_7801387-1_kaart.html")
