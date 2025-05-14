import pandas as pd

# Lae GTFS vormingus peatused (stops.txt) andmefail
stops = pd.read_csv('/data/csv failid/stops.txt')

# Filtreeri ainult Tartu Linnavalitsuse (Tartu LV) ja Tartu Maavalitsuse (Tartu MV) peatustega read
tartu_stops = stops[(stops['authority'] == 'Tartu LV') | (stops['authority'] == 'Tartu MV')]

# Salvesta kõik veerud CSV-faili, ilma duplikaate eemaldamata
tartu_stops.to_csv("/data/csv failid/tartu_stops.csv", index=False)
