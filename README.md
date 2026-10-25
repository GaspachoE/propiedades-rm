# Propiedades RM

Aplicación web hecha con Django que muestra un análisis de los precios de casas
usadas en venta en la Región Metropolitana de Santiago, con datos de marzo de 2023.

Cada análisis tiene su gráfico y un informe con la interpretación y una tabla de
datos de apoyo.

## Contenido

| Gráfico | Qué responde |
|---|---|
| Distribución de variables | ¿Cómo se distribuyen el precio, el área, los dormitorios y los baños? |
| Comunas con más publicaciones | ¿Dónde se concentra la oferta? |
| Precio por comuna y sector | ¿Qué comunas son las más caras? |
| Mapa de precios | Mapa interactivo con el precio promedio por comuna |
| Precio según dormitorios | ¿Cómo influye la cantidad de dormitorios? |
| Precio según estacionamientos | ¿Cómo influyen los estacionamientos? |
| Corredor por comuna y sector | ¿Influye contar con un corredor de propiedades? |
| Corredor: comparación global | Diferencia promedio entre propiedades con y sin corredor |
| Precio por m² según comuna | ¿Cómo cambia el precio por metro cuadrado según la comuna? |

## Requisitos

- Python 3.12 o superior (el proyecto se desarrolló con Python 3.14)
- Conexión a internet (el mapa carga la librería Bokeh desde internet)

## Instalación

Con Git:

```powershell
git clone https://github.com/GaspachoE/propiedades-rm.git
cd propiedades-rm
```

Sin Git: en esta página, pulsa **Code → Download ZIP**, descomprime la carpeta y
ábrela en una terminal.

Luego, dentro de la carpeta del proyecto, crea el entorno virtual e instala las
librerías:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

En macOS o Linux, el segundo comando es `source .venv/bin/activate`.

## Ejecución

```powershell
python manage.py runserver
```

Abre http://127.0.0.1:8000/ en el navegador. La página de inicio redirige al
primer gráfico, y desde el menú lateral se puede acceder a los demás.

Para detener el servidor, presiona `Ctrl + C` en la terminal.

## Estructura del proyecto

```
manage.py
requirements.txt
propiedades/          Configuración del proyecto Django
analisis/
├── data/
│   ├── CargaDatos.py     Carga y limpieza de los datos
│   ├── data1.csv         Dataset de propiedades
│   └── comunas.geojson   Mapa de las comunas
├── templates/analisis/   Plantillas HTML (menú lateral, gráficos e informes)
├── views.py              Una vista por gráfico, más los informes
└── urls.py               Rutas del sitio
```

## Rutas

- `/grafico1`, `/grafico2`, `/grafico3`, `/grafico5` ... `/grafico9`: gráficos
- `/mapa`: mapa interactivo (gráfico 4)
- `/informe/1` ... `/informe/9`: informe de cada gráfico

## Tecnologías

Django, pandas, matplotlib, geopandas, Bokeh y Bootstrap 5.
