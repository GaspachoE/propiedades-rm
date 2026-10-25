import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
import base64
from io import BytesIO     
from bokeh.plotting import figure
from bokeh.models import (
    GeoJSONDataSource,
    LabelSet,
    ColumnDataSource,
    Div,
    HoverTool
)
from bokeh.transform import factor_cmap
from bokeh.layouts import row
from bokeh.embed import components   
from bokeh.resources import CDN 

from pathlib import Path

RUTA_CSV = Path(__file__).resolve().parent / "data1.csv"
df = pd.read_csv(RUTA_CSV)

def figura_a_base64(figura):
    buffer = BytesIO()
    figura.savefig(buffer, format="png", dpi=110,
                   bbox_inches="tight")
    plt.close(figura)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

df_limpio=df.dropna(subset=["Dorms","Baths","Built Area","Total Area"])
df_limpio= df_limpio.fillna("Inexistente")
df_limpio["Parking"] = df_limpio["Parking"].replace("Inexistente", 0)
df_limpio["Parking"] = df_limpio["Parking"].astype(float) #######

df_limpio = df_limpio[df_limpio["Dorms"] <= 15]
Q1 = df_limpio["Baths"].quantile(0.25)
Q3 = df_limpio["Baths"].quantile(0.75)
IQR = Q3 - Q1
limite_inferior = Q1 - 1.5 * IQR
limite_superior = Q3 + 1.5 * IQR
outliers_baths = df_limpio[
    (df_limpio["Baths"] < limite_inferior) |
    (df_limpio["Baths"] > limite_superior)
]
df_limpio = df_limpio[
    (df_limpio["Baths"] >= limite_inferior) &
    (df_limpio["Baths"] <= limite_superior)
]
Q1 = df_limpio["Built Area"].quantile(0.25)
Q3 = df_limpio["Built Area"].quantile(0.75)
IQR = Q3 - Q1
limite_superior = Q3 + 1.5 * IQR
outliers_built = df_limpio[
    (df_limpio["Built Area"] <= 40) |
    (df_limpio["Built Area"] > limite_superior)
]
df_limpio = df_limpio[
    (df_limpio["Built Area"] > 40) &
    (df_limpio["Built Area"] <= limite_superior)
]
Q1 = df_limpio["Total Area"].quantile(0.25)
Q3 = df_limpio["Total Area"].quantile(0.75)
IQR = Q3 - Q1
limite_superior = Q3 + 1.5 * IQR
outliers_total = df_limpio[
    (df_limpio["Total Area"] <= 40) |
    (df_limpio["Total Area"] > limite_superior)
]
df_limpio = df_limpio[
    (df_limpio["Total Area"] > 40) &
    (df_limpio["Total Area"] <= limite_superior)
]

sector_map = {

    # Oriente
    'LasCondes': 'Oriente',
    'Vitacura': 'Oriente',
    'LoBarnechea': 'Oriente',
    'Providencia': 'Oriente',
    'LaReina': 'Oriente',
    'Ñuñoa': 'Oriente',

    # Centro
    'Santiago': 'Centro',
    'EstaciónCentral': 'Centro',
    'QuintaNormal': 'Centro',

    # Sur
    'SanMiguel': 'Sur',
    'SanJoaquín': 'Sur',
    'PedroAguirreCerda': 'Sur',
    'LaCisterna': 'Sur',
    'LaGranja': 'Sur',
    'SanRamón': 'Sur',
    'LaPintana': 'Sur',
    'ElBosque': 'Sur',
    'LoEspejo': 'Sur',
    'SanBernardo': 'Sur',

    # Suroriente
    'Macul': 'Suroriente',
    'Peñalolén': 'Suroriente',
    'LaFlorida': 'Suroriente',
    'PuenteAlto': 'Suroriente',
    'Pirque': 'Suroriente',
    'SanJosédeMaipo': 'Suroriente',

    # Norte
    'Huechuraba': 'Norte',
    'Conchalí': 'Norte',
    'Quilicura': 'Norte',
    'Renca': 'Norte',
    'Lampa': 'Norte',
    'Colina': 'Norte',
    'Tiltil': 'Norte',
    'Independencia': 'Norte',
    'Recoleta': 'Norte',

    # Poniente / Periferia
    'Maipú': 'Poniente / Periferia',
    'Pudahuel': 'Poniente / Periferia',
    'Cerrillos': 'Poniente / Periferia',
    'LoPrado': 'Poniente / Periferia',
    'CerroNavia': 'Poniente / Periferia',
    'PadreHurtado': 'Poniente / Periferia',
    'Peñaflor': 'Poniente / Periferia',
    'Talagante': 'Poniente / Periferia',
    'Buin': 'Poniente / Periferia',
    'Paine': 'Poniente / Periferia',
    'CaleradeTango': 'Poniente / Periferia',
    'IsladeMaipo': 'Poniente / Periferia',
    'Melipilla': 'Poniente / Periferia',
    'Curacaví': 'Poniente / Periferia',
    'ElMonte': 'Poniente / Periferia',
    'SanPedro': 'Poniente / Periferia',
    'MaríaPinto': 'Poniente / Periferia',
    'Alhué': 'Poniente / Periferia'
}
reemplazos = {
    "LaReina": "La Reina",
    "ElBosque": "El Bosque",
    "PedroAguirreCerda": "Pedro Aguirre Cerda",
    "LasCondes": "Las Condes",
    "LoBarnechea": "Lo Barnechea",
    "SanMiguel": "San Miguel",
    "LoEspejo": "Lo Espejo",
    "PadreHurtado": "Padre Hurtado",
    "EstaciónCentral": "Estación Central",
    "SanJosédeMaipo": "San José de Maipo",
    "CaleradeTango": "Calera de Tango",
    "LaGranja": "La Granja",
    "LaPintana": "La Pintana",
    "SanRamón": "San Ramón",
    "SanJoaquín": "San Joaquín",
    "LaCisterna": "La Cisterna",
    "SanBernardo": "San Bernardo",
    "LaFlorida": "La Florida",
    "PuenteAlto": "Puente Alto",
    "ElMonte": "El Monte",
    "QuintaNormal": "Quinta Normal",
    "IsladeMaipo": "Isla de Maipo",
    "CerroNavia": "Cerro Navia",
    "LoPrado": "Lo Prado"
}

sector_map_corregido = {reemplazos.get(c, c): s for c, s in sector_map.items()}

df_limpio["Sector"] = df_limpio["Comuna"].map(sector_map)   
df_limpio["Comuna"] = df_limpio["Comuna"].replace(reemplazos)  

df_limpio["Precio_m2"] = df_limpio["Price_CLP"] / df_limpio["Total Area"]

df_limpio["Rango_Dorms"] = pd.cut(df_limpio["Dorms"], bins=[0, 1, 3, 6, float("inf")],
                                  labels=["1", "2-3", "4-6", "+6"])
df_limpio["Rango_Parking"] = pd.cut(df_limpio["Parking"], bins=[-1, 0, 2, 4, float("inf")],
                                    labels=["0", "1-2", "3-4", "5+"])
df_limpio["Con_Corredor"] = np.where(df_limpio["Realtor"] == "Inexistente",
                                     "Sin Corredor", "Con Corredor")

df_limpio = df_limpio.copy()

df_limpio["Rango_Dorms"] = pd.cut(df_limpio["Dorms"], bins=[0, 1, 3, 6, float("inf")],
                                  labels=["1", "2-3", "4-6", "6+"])

# Si ya tienes Rango_Parking en este archivo, no lo repitas
df_limpio["Rango_Parking"] = pd.cut(df_limpio["Parking"], bins=[-1, 0, 2, 4, float("inf")],
                                    labels=["0", "1-2", "3-4", "5+"])

realtor_limpio = df_limpio["Realtor"].astype(str).str.strip().str.lower()
valores_vacios = ["", "nan", "none", "null", "na", "n/a", "-", "inexistente",
                  "sin corredor", "sin corretaje", "sin información", "sin informacion",
                  "no aplica", "no informado"]
df_limpio["Con_Corredor"] = np.where(df_limpio["Realtor"].isna() | realtor_limpio.isin(valores_vacios),
                                     "Sin Corredor", "Con Corredor")

COL_PRECIO = 'Price_UF'
