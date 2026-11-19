# Propiedades RM

Aplicación web hecha con Django que muestra un análisis de los precios de casas
usadas en venta en la Región Metropolitana de Santiago, con datos de marzo de 2023.

Cada análisis tiene su gráfico y un informe con la interpretación y una tabla de
datos de apoyo. Cada informe se puede descargar en PDF y en Excel.

## Integrantes

- Brad Bayuelo
- Gaspar Castillo
- Joaquín Donoso
- Alonso Neira

Profesor: Cristian Orlando García

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
| **Precio por comuna (dinámico)** | Precio promedio por comuna según filtros elegidos por el usuario |

### Gráfico dinámico

El gráfico "Precio por comuna (dinámico)" (`/grafico10`) permite filtrar por
**sector**, **rango de dormitorios** y **precio mínimo/máximo en UF**. Al presionar
"Aplicar", la vista de Django filtra los datos, los agrupa por comuna y vuelve a
dibujar el gráfico. Si ningún dato cumple los filtros, se muestra un mensaje.

Los filtros viajan en la URL (por ejemplo `/grafico10?sector=Oriente&dorms=4-6`),
por eso el gráfico, su informe (`/informe/10`), el PDF y el Excel siempre usan los
mismos datos.

### Descargas

Al final de cada informe hay dos botones: **Descarga en PDF** (título, análisis y
tabla, con reportlab) y **Descarga en Excel** (datos del gráfico, con pandas y
openpyxl). En el informe dinámico, ambos archivos respetan los filtros vigentes.

## Requisitos

- Python 3.12 o superior (el proyecto se desarrolló con Python 3.14)
- Conexión a internet (el mapa carga la librería Bokeh desde internet)

## Instalación

Pulsa **Code → Download ZIP**, descomprime la carpeta y
ábrela en una terminal (VS Code por ejemplo). También se puede clonar con
`git clone https://github.com/GaspachoE/propiedades-rm.git`.

Luego, dentro de la carpeta del proyecto, crea el entorno virtual e instala las
librerías:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

En macOS o Linux, el segundo comando es `source .venv/bin/activate`.

Dependencias principales (versiones completas en `requirements.txt`): Django,
pandas, numpy, matplotlib, geopandas, Bokeh, reportlab y openpyxl.

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
├── templates/analisis/   Plantillas HTML (menú lateral, gráficos, informes y filtros)
├── views.py              Una vista por gráfico, los informes y las descargas
└── urls.py               Rutas del sitio
```

## Rutas

- `/grafico1`, `/grafico2`, `/grafico3`, `/grafico5` ... `/grafico10`: gráficos
- `/mapa`: mapa interactivo (gráfico 4)
- `/informe/1` ... `/informe/10`: informe de cada gráfico
- `/informe/<n>/pdf` y `/informe/<n>/excel`: descargas de cada informe

## Tecnologías

Django, pandas, matplotlib, geopandas, Bokeh, reportlab, openpyxl y Bootstrap 5.
