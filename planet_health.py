import folium
import pandas as pd
from folium.plugins import HeatMap
from folium import IFrame
from geopy.geocoders import Nominatim
import os.path
from os import path


DATA_VRA = "files/VRA_102019.csv"
DATA_AEROPORTOS = "files/aeroportos.csv"

DATA_VOOS = "data/voos_dia.csv"
DATA_LOCATION = "data/loccations.csv"


class PlanetHealth(object):

    def __init__(self):
        if path.exists(DATA_VOOS):
            self.voos_dia = pd.read_csv(DATA_VOOS, delimiter=",")
            return

        df_voos = pd.read_csv(DATA_VRA, delimiter=";", usecols=['sg_icao_origem', 'sg_icao_destino', 'dt_partida_real'])
        df_aeroportos = pd.read_csv(DATA_AEROPORTOS, delimiter=";")
        df_voos = df_voos.rename(columns={"sg_icao_origem":"sg_origem", "sg_icao_destino":"sg_destino", "dt_partida_real":"data"})
        df_origen = df_aeroportos.rename(columns={"Sigla OACI":"sg_origem", "Descrição":"desc", "Cidade":"cidade_origem", "UF":"uf", "País":"pais_origem", "Continente":"continente"})
        result = df_voos.merge(df_origen, on='sg_origem')
        result = result[['sg_origem', 'cidade_origem', 'pais_origem', 'sg_destino', 'data']]
        df_destino = df_aeroportos.rename(columns={"Sigla OACI":"sg_destino", "Descrição":"desc", "Cidade":"cidade_destino", "UF":"uf", "País":"pais_destino", "Continente":"continente"})
        result = result.merge(df_destino, on='sg_destino')
        result = result[['sg_origem', 'cidade_origem', 'pais_origem', 'sg_destino', 'cidade_destino', 'pais_destino', 'data']]
        result['data'] = result['data'].str[:10]
        self.voos_dia = pd.DataFrame({'voos' : result.groupby(["cidade_origem", "sg_origem", "cidade_destino", "sg_destino", "data"]).size()}).reset_index()

        self.voos_dia.to_csv(DATA_VOOS)
        
    

    def _latitude(self, n):
        location = self.geolocator.geocode(n)
        
        if location is None:
            return None

        return float(location.latitude) if location.latitude is not None else None if location is not None else None

    def _longitude(self, n):
        location = self.geolocator.geocode(n)
        
        if location is None:
            return None

        return float(location.longitude) if location.longitude is not None else None if location is not None else None
    
    def processar(self, cidade):
        location = None
        latitude = None
        longitude = None
        self.geolocator = Nominatim(user_agent="Planet Health")        
        voos = self.voos_dia[(self.voos_dia['sg_origem'] == cidade.upper())|(self.voos_dia['cidade_origem'] == cidade.upper())]
        if path.exists(DATA_LOCATION):
            a  = pd.read_csv(DATA_LOCATION, delimiter=",")            
        else:            
            voos = voos.sort_values(by=['data']).reset_index()        
            vo = pd.DataFrame(data=self.voos_dia['cidade_destino'].unique())
            
            la = pd.DataFrame({"cidade_destino": vo[0], 'latitude' : vo[0].map(self._latitude), 'longitude' : vo[0].map(self._longitude)})        
            a = voos.merge(la, on='cidade_destino')
                        
            a.to_csv(DATA_LOCATION)

        a = a[(a['sg_origem'] == cidade.upper())|(a['cidade_origem'] == cidade.upper())]

        dados_map = a[['latitude','longitude', 'voos']].dropna()
        dados_map = dados_map.rename(columns={'latitude':'lat','longitude':'lng', 'voos':'weight'})
        dados_map.sort_values(by=['weight']).reset_index()

        if a['cidade_origem'].count() > 0:
            location = self.geolocator.geocode(cidade)
        if location is None:
            location = self.geolocator.geocode("São Paulo")
        
        latitude = location.latitude
        longitude = location.longitude

        if latitude is not None and longitude is not None:
            mapa = folium.Map(location=[latitude, longitude])

        HeatMap(data=dados_map.values.tolist()).add_to(mapa)
        return mapa._repr_html_()