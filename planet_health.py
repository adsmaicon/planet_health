import folium
import pandas as pd
from folium.plugins import HeatMap
from geopy.geocoders import Nominatim

def city(n):
    geolocator = Nominatim(user_agent="Planet Health")
    location = geolocator.geocode(n)
    
    if location is None:
        return ["", ""]

    lt = location.latitude if location.latitude is not None else '' if location is not None else ''
    lo = location.longitude if location.longitude is not None else '' if location is not None else ''
    return [n, lt, lo]


df_voos = pd.read_csv("VRA_102019.csv", delimiter=";", usecols=['sg_icao_origem', 'sg_icao_destino', 'dt_partida_real'])
df_aeroportos = pd.read_csv("aeroportos.csv", delimiter=";")
df_voos = df_voos.rename(columns={"sg_icao_origem":"sg_origem", "sg_icao_destino":"sg_destino", "dt_partida_real":"data"})

df_origen = df_aeroportos.rename(columns={"Sigla OACI":"sg_origem", "Descrição":"desc", "Cidade":"cidade_origem", "UF":"uf", "País":"pais_origem", "Continente":"continente"})
result = df_voos.merge(df_origen, on='sg_origem')
result = result[['sg_origem', 'cidade_origem', 'pais_origem', 'sg_destino', 'data']]

df_destino = df_aeroportos.rename(columns={"Sigla OACI":"sg_destino", "Descrição":"desc", "Cidade":"cidade_destino", "UF":"uf", "País":"pais_destino", "Continente":"continente"})
df_destino.head()
result = result.merge(df_destino, on='sg_destino')

result = result[['sg_origem', 'cidade_origem', 'pais_origem', 'sg_destino', 'cidade_destino', 'pais_destino', 'data']]
result['data'] = result['data'].str[:10]

voos_dia = pd.DataFrame({'voos' : result.groupby(["cidade_origem", "cidade_destino", "data"]).size()}).reset_index()
voos_dia = voos_dia.sort_values(by=['data']).reset_index()

geolocator = Nominatim(user_agent="Planet Health")
vo = pd.DataFrame(data=voos_dia['cidade_destino'].unique())
ivo = vo[0].map(lambda x: city(x))
ivo