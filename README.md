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

## Enlaces de entrega

- Sitio desplegado: _(pendiente: dirección del sitio)_
- Video 1, despliegue del software: _(pendiente: enlace)_
- Video 2, presentación del software y explicación del código: _(pendiente: enlace)_

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
tabla, con reportlab) y **Descarga en Excel** (la misma tabla del reporte, con
pandas y openpyxl, con los valores guardados como números). La página, el PDF y el
Excel salen de la misma función (`tabla_numerica` en `views.py`), por eso siempre
muestran los mismos datos. En el informe dinámico, ambos archivos respetan los
filtros vigentes.

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

Después crea la base de datos SQLite y carga los datos (solo la primera vez):

```powershell
python manage.py migrate
python manage.py cargar_datos
```

- `migrate` crea el archivo `db.sqlite3` con la tabla de propiedades.
- `cargar_datos` lee `analisis/data/data1.csv` y guarda sus 9.291 filas en esa tabla.

## Base de datos

El sitio lee los datos desde una base de datos **SQLite** (`db.sqlite3`), no
directamente del CSV:

1. **Modelo** (`analisis/models.py`): la clase `Propiedad` define la tabla, con un
   campo por cada columna del CSV (precio, comuna, dormitorios, baños, áreas,
   estacionamientos, corredor...).
2. **Carga** (`analisis/management/commands/cargar_datos.py`): comando que lee el CSV
   con pandas y guarda todas las filas con `bulk_create`. Si se vuelve a ejecutar,
   reemplaza los datos (no quedan duplicados).
3. **Lectura** (`analisis/data/CargaDatos.py`): `leer_base_de_datos()` consulta la
   tabla con el ORM de Django (`Propiedad.objects.values(...)`) y la convierte en un
   DataFrame. `obtener_datos()` aplica la limpieza (nulos y outliers) y crea las
   columnas derivadas (sector, rangos, precio por m²). El resultado se guarda en
   memoria con `lru_cache`, así la base se consulta una sola vez y no en cada visita.

Para revisar la tabla desde el navegador se puede crear un usuario con
`python manage.py createsuperuser` y entrar a `/admin`.

Dependencias principales (versiones completas en `requirements.txt`): Django,
pandas, numpy, matplotlib, geopandas, Bokeh, reportlab y openpyxl.

## Ejecución

```powershell
python manage.py runserver
```

Abre http://127.0.0.1:8000/ en el navegador. La página de inicio redirige al
primer gráfico, y desde el menú lateral se puede acceder a los demás.

Para detener el servidor, presiona `Ctrl + C` en la terminal.

## Despliegue

Sitio publicado en: **http://3.218.18.208:8000**

Esta IP es Elástica, así que se mantiene aún si se cierra la Instancia en AWS.

El sitio se despliega en una instancia **Amazon EC2** con Ubuntu. La base de datos
SQLite es un archivo (`db.sqlite3`) que vive en el disco de la misma instancia, así
que no se necesita un servicio de base de datos aparte.

### 1. Crear la instancia EC2

1. En la consola de AWS, ir a **EC2 → Launch instance**.
2. Elegir **Ubuntu Server 24.04 LTS** y el tipo `t2.micro` o `t3.micro`.
3. Crear o elegir un **key pair** (archivo `.pem`) para conectarse por SSH.
4. En **Network settings → Security group**, agregar estas reglas de entrada:
   - SSH, puerto **22**, origen "My IP".
   - Custom TCP, puerto **8000**, origen `0.0.0.0/0` (para entrar al sitio desde cualquier navegador).
5. Lanzar la instancia y copiar su **IPv4 pública** (En nuestro caso, `3.218.18.208`).

### 2. Conectarse e instalar el proyecto

```bash
ssh -i mi-llave.pem ubuntu@54.123.45.67

sudo apt update
sudo apt install -y python3-venv git
git clone https://github.com/GaspachoE/propiedades-rm.git
cd propiedades-rm
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Si la instalación se cae por falta de memoria (instancias de 1 GB), crear un
archivo de intercambio y repetir el `pip install`:

```bash
sudo fallocate -l 2G /swapfile && sudo chmod 600 /swapfile
sudo mkswap /swapfile && sudo swapon /swapfile
```

### 3. Crear la base de datos SQLite en la instancia

```bash
python manage.py migrate        # crea db.sqlite3 y la tabla de propiedades
python manage.py cargar_datos   # carga las 9.291 propiedades del CSV
```

### 4. Configurar Django para la dirección del servidor

En `propiedades/settings.py`, `ALLOWED_HOSTS` y `DEBUG` se leen desde variables de
entorno, así que no hay que editar el código. Django solo responde a las
direcciones que están en `ALLOWED_HOSTS`:

```bash
export DJANGO_ALLOWED_HOSTS=.3.218.18.208  # IP pública de la instancia
export DJANGO_DEBUG=False                  # no mostrar errores internos al público
```

### 5. Iniciar el servidor

```bash
nohup python manage.py runserver 0.0.0.0:8000 --insecure > servidor.log 2>&1 &
```

- `0.0.0.0` hace que el servidor acepte conexiones desde fuera de la instancia.
- `--insecure` permite servir los archivos estáticos del panel `/admin` con `DEBUG=False`.
- `nohup ... &` mantiene el servidor funcionando al cerrar la conexión SSH.

Para detenerlo: `pkill -f runserver`.

### 6. Comprobar desde un navegador externo

Abrir `http://54.123.45.67:8000` desde otro computador o desde el celular, y
revisar los gráficos, el gráfico dinámico con sus filtros, los reportes y las
descargas en PDF y Excel.

### Actualizar el sitio después de un cambio

```bash
cd propiedades-rm && source .venv/bin/activate
git pull
python manage.py migrate
pkill -f runserver
nohup python manage.py runserver 0.0.0.0:8000 --insecure > servidor.log 2>&1 &
```

Las variables `DJANGO_ALLOWED_HOSTS` y `DJANGO_DEBUG` se pierden al cerrar la
sesión SSH: hay que volver a ejecutar los `export` antes de reiniciar el servidor.

## Estructura del proyecto

```
manage.py
requirements.txt
db.sqlite3            Base de datos (se crea con "migrate", no viene en el repositorio)
propiedades/          Configuración del proyecto Django
analisis/
├── data/
│   ├── CargaDatos.py     Lectura de la base de datos y limpieza de los datos
│   ├── data1.csv         Dataset original (se carga en la base con cargar_datos)
│   └── comunas.geojson   Mapa de las comunas
├── management/commands/
│   └── cargar_datos.py   Comando que carga el CSV en la base de datos
├── migrations/           Migraciones del modelo Propiedad
├── templates/analisis/   Plantillas HTML (menú lateral, gráficos, reportes y filtros)
├── admin.py              Tabla de propiedades en el panel /admin
├── models.py             Modelo Propiedad (tabla de la base de datos)
├── views.py              Una vista por gráfico, los informes y las descargas
└── urls.py               Rutas del sitio
```

## Rutas

- `/grafico1`, `/grafico2`, `/grafico3`, `/grafico5` ... `/grafico10`: gráficos
- `/mapa`: mapa interactivo (gráfico 4)
- `/informe/1` ... `/informe/10`: informe de cada gráfico
- `/informe/<n>/pdf` y `/informe/<n>/excel`: descargas de cada informe
- `/admin`: panel de administración de Django (tabla de propiedades)

El menú lateral tiene dos secciones: **Gráficos** (cada gráfico con su informe) y
**Reportes** (acceso directo a los diez reportes).

## Tecnologías

Django, SQLite, pandas, matplotlib, geopandas, Bokeh, reportlab, openpyxl, Bootstrap 5 y AWS EC2.
