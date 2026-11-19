import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
import base64
from io import BytesIO
from functools import lru_cache
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

from django.db.utils import OperationalError

from analisis.models import COLUMNAS_CSV, Propiedad

COL_PRECIO = 'Price_UF'


def figura_a_base64(figura):
    buffer = BytesIO()
    figura.savefig(buffer, format="png", dpi=110,
                   bbox_inches="tight")
    plt.close(figura)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


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


def leer_base_de_datos():
    """Lee la tabla Propiedad de SQLite y la devuelve como DataFrame,
    con los mismos nombres de columna que tenía el CSV original."""
    campos = list(COLUMNAS_CSV.values())
    try:
        df = pd.DataFrame.from_records(Propiedad.objects.values(*campos), columns=campos)
    except OperationalError:
        # Pasa si db.sqlite3 no existe o no tiene la tabla (falta "migrate")
        raise RuntimeError(
            "No se encontró la tabla de propiedades en db.sqlite3. Ejecuta primero: "
            "python manage.py migrate  y luego  python manage.py cargar_datos"
        )
    if df.empty:
        raise RuntimeError(
            "La base de datos no tiene propiedades. Ejecuta primero: "
            "python manage.py migrate  y luego  python manage.py cargar_datos"
        )
    nombres_originales = {campo: columna for columna, campo in COLUMNAS_CSV.items()}
    df = df.rename(columns=nombres_originales)
    # Los NULL de la base de datos llegan como None: se pasan a NaN como en el CSV
    numericas = ["Dorms", "Baths", "Built Area", "Total Area", "Parking"]
    df[numericas] = df[numericas].astype(float)
    return df


@lru_cache(maxsize=1)
def obtener_datos():
    """Devuelve df_limpio: los datos de la base de datos ya limpios.

    Se calcula la primera vez que una vista lo pide y queda guardado en memoria
    (lru_cache), así no se consulta la base de datos en cada visita.
    No se ejecuta al importar el archivo, para que "migrate" funcione aunque la
    tabla todavía no exista.
    """
    df = leer_base_de_datos()

    # --- Limpieza de nulos ---
    df_limpio = df.dropna(subset=["Dorms", "Baths", "Built Area", "Total Area"])
    df_limpio = df_limpio.fillna("Inexistente")
    df_limpio["Parking"] = df_limpio["Parking"].replace("Inexistente", 0)
    df_limpio["Parking"] = df_limpio["Parking"].astype(float)

    # --- Outliers (método IQR) ---
    df_limpio = df_limpio[df_limpio["Dorms"] <= 15]
    Q1 = df_limpio["Baths"].quantile(0.25)
    Q3 = df_limpio["Baths"].quantile(0.75)
    IQR = Q3 - Q1
    limite_inferior = Q1 - 1.5 * IQR
    limite_superior = Q3 + 1.5 * IQR
    df_limpio = df_limpio[
        (df_limpio["Baths"] >= limite_inferior) &
        (df_limpio["Baths"] <= limite_superior)
    ]
    Q1 = df_limpio["Built Area"].quantile(0.25)
    Q3 = df_limpio["Built Area"].quantile(0.75)
    IQR = Q3 - Q1
    limite_superior = Q3 + 1.5 * IQR
    df_limpio = df_limpio[
        (df_limpio["Built Area"] > 40) &
        (df_limpio["Built Area"] <= limite_superior)
    ]
    Q1 = df_limpio["Total Area"].quantile(0.25)
    Q3 = df_limpio["Total Area"].quantile(0.75)
    IQR = Q3 - Q1
    limite_superior = Q3 + 1.5 * IQR
    df_limpio = df_limpio[
        (df_limpio["Total Area"] > 40) &
        (df_limpio["Total Area"] <= limite_superior)
    ].copy()

    # --- Columnas derivadas ---
    df_limpio["Sector"] = df_limpio["Comuna"].map(sector_map)
    df_limpio["Comuna"] = df_limpio["Comuna"].replace(reemplazos)

    df_limpio["Precio_m2"] = df_limpio["Price_CLP"] / df_limpio["Total Area"]

    df_limpio["Rango_Dorms"] = pd.cut(df_limpio["Dorms"], bins=[0, 1, 3, 6, float("inf")],
                                      labels=["1", "2-3", "4-6", "6+"])
    df_limpio["Rango_Parking"] = pd.cut(df_limpio["Parking"], bins=[-1, 0, 2, 4, float("inf")],
                                        labels=["0", "1-2", "3-4", "5+"])

    realtor_limpio = df_limpio["Realtor"].astype(str).str.strip().str.lower()
    valores_vacios = ["", "nan", "none", "null", "na", "n/a", "-", "inexistente",
                      "sin corredor", "sin corretaje", "sin información", "sin informacion",
                      "no aplica", "no informado"]
    df_limpio["Con_Corredor"] = np.where(df_limpio["Realtor"].isna() | realtor_limpio.isin(valores_vacios),
                                         "Sin Corredor", "Con Corredor")

    return df_limpio
