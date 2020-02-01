import pandas as pd
import numpy as np
from IPython.display import display
import datetime
from tqdm import tqdm
import os
#import folium
from folium import Map,Marker,LayerControl,CustomIcon
from folium.plugins import HeatMap


#import matplotlib.pyplot as plt
#import seaborn as sns
#from folium import plugins
#from folium.plugins import HeatMap #レイヤーの設定に用いている


icon_ramen="ramen.png"

df=pd.read_csv('active_shops_with_latlon.csv')
print(df.shape)
print(df.head())

m=Map(location=[df['lat'].mean(), df['lon'].mean()],zoom_start=5)

HeatMap(df[['lat', 'lon','review_score']].values.tolist(),name="ヒートマップ").add_to(m)

for row in df.itertuples():
    Marker(location=(row.lat, row.lon),
           popup='<a href="{url}" target="_blank">{name}</a>'.format(url=row.url,name=row.name),
           icon=CustomIcon(icon_ramen,icon_size=(20,20), popup_anchor=(0,0)),
           ).add_to(m)


LayerControl().add_to(m)

m.save('heatmap.html')
