from django.shortcuts import render
from .data.CargaDatos import *
import matplotlib
matplotlib.use("Agg") # Dibujar sin abrir una ventana gráfica
from pathlib import Path


def grafico1(request):
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))

    # Histograma de precio (UF)
    axes[0, 0].hist(df_limpio["Price_UF"], bins=40, color="steelblue", edgecolor="white")
    axes[0, 0].set_title("Distribucion del precio (UF)", fontweight="bold")
    axes[0, 0].set_xlabel("Precio (UF)")
    axes[0, 0].set_ylabel("Cantidad de propiedades")

    # Histograma de area construida
    axes[0, 1].hist(df_limpio["Built Area"], bins=40, color="darkorange", edgecolor="white")
    axes[0, 1].set_title("Distribución del area construida", fontweight="bold")
    axes[0, 1].set_xlabel("area construida (m2)")
    axes[0, 1].set_ylabel("Cantidad de propiedades")

    # Boxplot de dormitorios
    axes[1, 0].boxplot(df_limpio["Dorms"].dropna(), vert=True)
    axes[1, 0].set_title("Dispersion de dormitorios", fontweight="bold")
    axes[1, 0].set_ylabel("Cantidad de dormitorios")

    # Boxplot de baños
    axes[1, 1].boxplot(df_limpio["Baths"].dropna(), vert=True)
    axes[1, 1].set_title("Dispersion de baños", fontweight="bold")
    axes[1, 1].set_ylabel("Cantidad de baños")

    fig.tight_layout()
    grafico = figura_a_base64(fig)
    return render(request, "analisis/grafico_simple.html",
              {"grafico": grafico, "titulo": "Distribución de variables", "numero": 1})


def grafico2(request):
    top10_comunas = df_limpio["Comuna"].value_counts().head(10)

    fig = plt.figure(figsize=(10, 5))
    top10_comunas.sort_values().plot(kind="barh")
    plt.title("Top 10 comunas con más publicaciones de venta", fontweight="bold")
    plt.xlabel("Cantidad de propiedades publicadas")
    plt.ylabel("Comuna")
    plt.tight_layout()
    grafico = figura_a_base64(fig)
    return render(request, "analisis/grafico_simple.html",
              {"grafico": grafico, "titulo": "Comunas con más publicaciones", "numero": 2})

def grafico3(request):
    sectores = [
    s
    for s in df_limpio['Sector'].unique()
    if s != 'Sin clasificar']

    COL_PRECIO = "Price_UF"
    n_filas = int(np.ceil(len(sectores) / 2))

    fig, axes = plt.subplots(n_filas, 2, figsize=(16, 5.5 * n_filas))
    axes = np.array(axes).reshape(-1)

    promedio_general = df_limpio[COL_PRECIO].mean()
    rng = np.random.default_rng(0)   # el jitter queda igual en cada recarga

    for ax, sector in zip(axes, sectores):
        df_sector = df_limpio[df_limpio["Sector"] == sector]
        prom_comuna = df_sector.groupby("Comuna")[COL_PRECIO].mean().sort_values()
        prom_sector = df_sector[COL_PRECIO].mean()
        pos_map = {comuna: i for i, comuna in enumerate(prom_comuna.index)}

        # Puntos individuales con jitter
        x_jitter = df_sector["Comuna"].map(pos_map) + rng.uniform(-0.18, 0.18, size=len(df_sector))
        ax.scatter(x_jitter, df_sector[COL_PRECIO], alpha=0.35, s=18,
                   color="steelblue", label="Precio individual", zorder=1)

        # Promedio de cada comuna
        for comuna, x_pos in pos_map.items():
            ax.hlines(y=prom_comuna[comuna], xmin=x_pos - 0.28, xmax=x_pos + 0.28,
                      color="darkorange", linewidth=3, zorder=3,
                      label="Promedio por comuna" if x_pos == 0 else None)

        # Promedio del sector
        ax.axhline(prom_sector, color="crimson", linestyle="--", linewidth=1.8, zorder=2,
                   label=f"Promedio del sector ({prom_sector:,.0f} UF)")

        ax.set_xticks(range(len(prom_comuna)))
        ax.set_xticklabels(prom_comuna.index, rotation=45, ha="right", fontsize=9)
        ax.set_xlabel("Comuna", fontsize=10)
        ax.set_ylabel("Precio (UF)", fontsize=10)
        ax.set_title(f"Sector {sector} — Precio vs. Promedio", fontsize=12, fontweight="bold")
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:,.0f}"))
        ax.grid(axis="y", linestyle=":", alpha=0.4)
        ax.legend(loc="upper left", fontsize=8, framealpha=0.9)

    # Quitar los cuadros sobrantes si los sectores son impares
    for ax in axes[len(sectores):]:
        fig.delaxes(ax)

    fig.suptitle(f"Precio de propiedades ({COL_PRECIO}) por Comuna y Sector\n"
                 f"Promedio general (todas las comunas): {promedio_general:,.0f} UF",
                 fontsize=15, fontweight="bold", y=1.02)
    fig.tight_layout()

    return render(request, "analisis/grafico_simple.html",
              {"grafico": figura_a_base64(fig), "titulo": "Precio por comuna y sector", "numero": 3})

def grafico4(request):
    mapa = gpd.read_file(Path(__file__).resolve().parent / "data" / "comunas.geojson")
    mapa_rm = mapa[mapa["Region"] == "Región Metropolitana de Santiago"].copy()

    # eliminar comunas sin registros
    mapa_rm = mapa_rm[~mapa_rm["Comuna"].isin(["Alhué", "San Pedro", "María Pinto"])].copy()

    # CAMBIO: en el notebook df_limpio ya tenía las comunas con espacios.
    # Aquí trabajamos sobre una copia para no alterar los otros gráficos.
    df_mapa = df_limpio.copy()
    df_mapa["Comuna"] = df_mapa["Comuna"].replace(reemplazos)

    #sector
    mapa_rm["Sector"] = mapa_rm["Comuna"].map(sector_map_corregido)

    # precio promedio UF por comuna
    promedios_comuna = (df_mapa.groupby("Comuna")["Price_UF"].mean().reset_index())  # CAMBIO: df_mapa
    mapa_rm = mapa_rm.merge(promedios_comuna, on="Comuna", how="left")

    #pasarlo a otro formato
    geo_source = GeoJSONDataSource(geojson=mapa_rm.to_json())

    centros = mapa_rm.geometry.representative_point()
    labels = ColumnDataSource(data={
        "x": centros.x.tolist(),
        "y": centros.y.tolist(),
        "Comuna": mapa_rm["Comuna"].tolist()
    })

    # Asignar color por sector
    sectores = [
        "Oriente",
        "Centro",
        "Sur",
        "Suroriente",
        "Norte",
        "Poniente / Periferia"
    ]

    colores = [
        "#4C78A8",
        "#F2CF5B",
        "#E45756",
        "#72B7B2",
        "#59A14F",
        "#B279A2"
    ]

    # Crear mapa
    p = figure(
        title="Comunas de la Región Metropolitana por Sector",
        width=900,
        height=700,
        tools="pan,wheel_zoom,reset"
    )

    poligonos = p.patches(
        xs="xs",
        ys="ys",
        source=geo_source,

        fill_color=factor_cmap(
            "Sector",
            palette=colores,
            factors=sectores
        ),

        fill_alpha=0.8,
        line_color="black",
        line_width=1
    )

    hover = HoverTool(
        renderers=[poligonos],
        tooltips=[
            ("Comuna", "@Comuna"),
            ("Precio promedio", "@Price_UF{0,0} UF")
        ]
    )
    p.add_tools(hover)

    # Nombre de comunas
    comuna_labels = LabelSet(
        x="x",
        y="y",
        text="Comuna",
        source=labels,
        text_font_size="8pt",
        text_align="center"
    )

    p.add_layout(comuna_labels)

    # Precio promedio UF por sector
    df_sector = df_mapa.copy()   # CAMBIO: df_mapa en vez de df_limpio
    df_sector["Sector"] = df_sector["Comuna"].map(
        sector_map_corregido
    )

    promedios_sector = (df_sector.dropna(subset=["Sector", "Price_UF"]).groupby("Sector")["Price_UF"].mean())

    #Cuadricula
    p.background_fill_color = "#E8F1F5"
    p.xgrid.grid_line_color = "white"
    p.xgrid.grid_line_alpha = 0.8
    p.xgrid.grid_line_width = 1
    p.ygrid.grid_line_color = "white"
    p.ygrid.grid_line_alpha = 0.8
    p.ygrid.grid_line_width = 1

    #Leyenda
    html = """
    <div style="
        background-color:white;
        padding:15px;
        border:1px solid #cccccc;
        border-radius:8px;
        font-family:Arial;
    ">

    <h3 style="margin-top:0;">
    Precio promedio por sector
    </h3>
    """

    for sector, color in zip(sectores, colores):

        if sector in promedios_sector.index:

            precio = promedios_sector[sector]

            html += f"""
            <div style="
                margin-bottom:10px;
                font-size:13px;
            ">

            <span style="
                display:inline-block;
                width:14px;
                height:14px;
                background-color:{color};
                border:1px solid black;
                margin-right:6px;
                vertical-align:middle;
            "></span>

            <b>{sector}</b><br>

            <span style="
                margin-left:22px;
                color:#555;
            ">
            {precio:,.0f} UF
            </span>

            </div>
            """
    html += "</div>"
    leyenda = Div(
        text=html,
        width=250,
        height=300
    )

    #Mostrar
    layout = row(p, leyenda)

    # CAMBIO: en vez de show(layout), se obtienen el script y el div para el template
    script, div = components(layout)
    contexto = {"script": script, "div": div, "recursos": CDN.render()}
    return render(request, "analisis/mapa.html", contexto)

def grafico5(request):
    fig, ax = plt.subplots(figsize=(8, 4.8))
    #Una vez creados los rangos observamos la relación con el precio final
    promedio_dorms = df_limpio.groupby("Rango_Dorms", observed=True)["Price_CLP"].mean()
    promedio_dorms.plot(
        kind="bar",
        ax=ax,
        xlabel="Cantidad de dormitorios",
        ylabel="Precio promedio (en millones de CLP)",
        title="Precio promedio según cantidad de dormitorios"
    )
    plt.xticks(rotation=0)
    grafico = figura_a_base64(fig)
    return render(request, "analisis/grafico_simple.html",
              {"grafico": grafico, "titulo": "Precio según dormitorios", "numero": 5})


def grafico6(request):
    orden_parking = ["0", "1", "2", "3", "4", "5+"]
    n_cols = 2
    n_rows = 3

    sectores = ["Oriente", "Centro", "Sur", "Suroriente", "Norte", "Poniente / Periferia"]

    datos = df_limpio.copy()
    cantidad = pd.to_numeric(datos["Parking"], errors="coerce")

    validos = cantidad.notna() & (cantidad >= 0) & (cantidad % 1 == 0)
    datos = datos.loc[validos].copy()
    cantidad = cantidad.loc[validos]

    datos["Grupo_Parking"] = (cantidad.clip(upper=5).astype(int).astype(str).replace({"5": "5+"}))

    precio_por_sector = (
        datos.groupby(["Sector", "Grupo_Parking"])["Price_CLP"]
        .mean()
        .unstack("Grupo_Parking")
        .reindex(index=sectores, columns=orden_parking)
    )

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(13, 5 * n_rows))
    axes = np.array(axes).reshape(-1)

    for i, sector in enumerate(sectores):
        ax = axes[i]
        precios = precio_por_sector.loc[sector]
        x = np.arange(len(orden_parking))

        ax.plot(x, precios.values, marker="o", linewidth=2)
        ax.set_xticks(x)
        ax.set_xticklabels(orden_parking)
        ax.set_title(f"Sector {sector}", fontsize=11, fontweight="bold")
        ax.set_xlabel("Cantidad de Estacionamientos")
        ax.set_ylabel("Precio Promedio (CLP)")
        ax.ticklabel_format(axis="y", style="plain")
        ax.margins(y=0.15)

        for posicion, valor in enumerate(precios.values):
            if pd.notna(valor):
                ax.annotate(
                    f"{valor:,.0f}",
                    xy=(posicion, valor), xytext=(0, 8), textcoords="offset points", ha="center", fontsize=8)

        ax.grid(axis="y", linestyle=":", alpha=0.4)

    for j in range(len(sectores), len(axes)): fig.delaxes(axes[j])

    fig.suptitle("Precio Promedio según Cantidad de Estacionamientos, por Sector", fontsize=14, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.96])

    grafico = figura_a_base64(fig)

    return render(request, "analisis/grafico_simple.html", {"grafico": grafico, "titulo": "Precio según estacionamientos", "numero": 6})

def grafico7(request):  
    sectores = [s for s in df_limpio['Sector'].unique() if s != 'Sin clasificar']
    orden_sectores = ['Oriente', 'Centro', 'Sur', 'Suroriente', 'Norte', 'Poniente / Periferia']
    sectores = [s for s in orden_sectores if s in sectores] + [s for s in sectores if s not in orden_sectores]

    n_sectores = len(sectores)
    n_cols = 2
    n_rows = int(np.ceil(n_sectores / n_cols))

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 5.5 * n_rows))
    axes = np.array(axes).reshape(-1)

    # Un subplot por sector, con barras Con/Sin Corredor por comuna
    for i, sector in enumerate(sectores):
        ax = axes[i]
        df_sector = df_limpio[df_limpio['Sector'] == sector]

        tabla = df_sector.groupby(['Comuna', 'Con_Corredor'])[COL_PRECIO].mean().unstack()
        tabla = tabla.reindex(columns=['Sin Corredor', 'Con Corredor'])
        tabla = tabla.reindex(tabla.mean(axis=1).sort_values().index)

        comunas_orden = tabla.index.tolist()
        x = np.arange(len(comunas_orden))
        ancho = 0.38

        valores_sin = tabla['Sin Corredor'].values
        valores_con = tabla['Con Corredor'].values

        ax.bar(x - ancho / 2, valores_sin, width=ancho, color='seagreen', label='Sin Corredor')
        ax.bar(x + ancho / 2, valores_con, width=ancho, color='steelblue', label='Con Corredor')

        promedio_sector = df_sector[COL_PRECIO].mean()
        ax.axhline(
            promedio_sector, color='crimson', linestyle='--', linewidth=1.5,
            label=f'Promedio del sector ({promedio_sector:,.0f} UF)'
        )

        ax.set_xticks(x)
        ax.set_xticklabels(comunas_orden, rotation=45, ha='right', fontsize=9)
        ax.set_xlabel('Comuna', fontsize=10)
        ax.set_ylabel('Precio Promedio (UF)', fontsize=10)
        ax.set_title(f'Sector {sector} — Precio Promedio: Con vs. Sin Corredor', fontsize=12, fontweight='bold')

        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:,.0f}'))

        ax.grid(axis='y', linestyle=':', alpha=0.4)
        ax.legend(loc='upper left', fontsize=8, framealpha=0.9)

    # Ocultar subplots sobrantes si el número de sectores es impar
    for j in range(n_sectores, len(axes)):
        fig.delaxes(axes[j])

    fig.suptitle(
        f'¿Influye el corredor de propiedades en el precio ({COL_PRECIO})?\n'
        f'Comparación por Comuna y Sector',
        fontsize=15, fontweight='bold', y=1.02
    )
    plt.tight_layout()
    grafico = figura_a_base64(fig)
    return render(request, "analisis/grafico_simple.html",
              {"grafico": grafico, "titulo": "Corredor por comuna y sector", "numero": 7})

def grafico8(request):
    precio_promedio = df_limpio.groupby('Con_Corredor')[COL_PRECIO].mean().reindex(['Con Corredor', 'Sin Corredor'])
    diferencia_pct = (precio_promedio['Con Corredor'] / precio_promedio['Sin Corredor'] - 1) * 100

    colores = ['purple', 'orange']

    fig, ax = plt.subplots(figsize=(7, 7))

    # Torta: cada porción representa el promedio de uno de los dos grupos
    ax.pie(
        precio_promedio.values,
        labels=precio_promedio.index,
        autopct=lambda pct: f'{pct:.1f}%\n({pct/100 * precio_promedio.sum():,.0f} UF)',
        colors=colores,
        startangle=90,
        wedgeprops={'edgecolor': 'white', 'linewidth': 1.5},
        textprops={'fontsize': 10}
    )

    ax.set_title(
        f'Precio Promedio: Con Corredor vs. Sin Corredor\n'
        f'(Con Corredor es {diferencia_pct:+.1f}% respecto a Sin Corredor)',
        fontsize=13, fontweight='bold'
    )

    plt.tight_layout()
    grafico = figura_a_base64(fig)
    return render(request, "analisis/grafico_simple.html",
              {"grafico": grafico, "titulo": "Corredor: comparación global", "numero": 8})

def grafico9(request):
    fig, ax = plt.subplots(figsize=(10, 12))
    df_limpio["Precio_m2"] = df_limpio["Price_CLP"] / df_limpio["Total Area"]
    precio_m2_comuna = df_limpio.groupby("Comuna")["Precio_m2"].mean().sort_values(ascending=False)
    precio_m2_comuna.plot(
        kind="barh",
        ax=ax,
        xlabel="Precio promedio por m² (CLP)",
        ylabel="Comuna",
        title="Precio promedio por m² según comuna"
    )
    ax.grid(axis="x", linestyle="--", alpha=0.5)
    grafico = figura_a_base64(fig)
    return render(request, "analisis/grafico_simple.html",
              {"grafico": grafico, "titulo": "Precio por m² según comuna", "numero": 9})


#----------------------------------------
# Desde aqui hasta abajo fue hecho completamente con IA
#----------------------------------------
from django.http import Http404

ORDEN_SECTORES = ["Oriente", "Centro", "Sur", "Suroriente", "Norte", "Poniente / Periferia"]

# Un informe por gráfico. El número es el mismo de grafico1 ... grafico9
INFORMES = {
    1: {
        "titulo": "Distribución de variables",
        "pregunta": "¿Cómo se distribuyen el precio, el área y la cantidad de dormitorios y baños?",
        "grafico": "grafico1",
        "analisis": [
            "El precio muestra una fuerte asimetría positiva incluso después de la limpieza: la mayoría de las propiedades se concentra en precios bajos y medios, y un grupo pequeño de propiedades de alto valor estira el promedio por sobre la mediana.",
            "El área construida sigue un patrón similar, concentrada en rangos habitables típicos (aprox. 70 a 250 m²) tras el filtro de outliers.",
            "Dormitorios y baños tienen poca dispersión, con medianas en 4 y 2 respectivamente.",
        ],
    },
    2: {
        "titulo": "Comunas con más publicaciones",
        "pregunta": "¿Dónde se concentra la oferta de viviendas usadas?",
        "grafico": "grafico2",
        "analisis": [
            "Puente Alto, Maipú y Las Condes concentran la mayor cantidad de publicaciones, lo que indica que son las comunas con mayor dinamismo en el mercado de venta de casas usadas de este dataset.",
            "Una parte importante de las publicaciones no tiene corredor asociado, y ninguna corredora domina el mercado: casi 250 corredoras distintas, por lo que el mercado está fragmentado entre muchos actores.",
        ],
    },
    3: {
        "titulo": "Precio por comuna y sector",
        "pregunta": "¿Qué comunas tienen el costo de vivienda más elevado?",
        "grafico": "grafico3",
        "analisis": [
            "La comuna es la variable que más mueve el precio. Hay comunas donde el promedio ronda las 2.000 a 2.600 UF (La Pintana, San Ramón) y otras donde llega a 16.800 a 20.200 UF (Las Condes, Providencia, Lo Barnechea).",
            "El sector Oriente promedia alrededor de 16.400 UF, entre 2,4 y 3,9 veces el promedio de cada uno de los demás sectores.",
        ],
    },
    4: {
        "titulo": "Mapa de precios por comuna",
        "pregunta": "¿Cómo se distribuye el precio promedio en el territorio?",
        "grafico": "grafico4",
        "analisis": [
            "El mapa colorea cada comuna según su sector y permite ver el precio promedio en UF al pasar el cursor.",
            "Refuerza lo visto en el gráfico anterior: las cinco comunas más caras (Lo Barnechea, Vitacura, Providencia, Las Condes y La Reina) pertenecen al sector Oriente, y la tabla muestra también las cinco más baratas.",
        ],
    },
    5: {
        "titulo": "Precio según dormitorios",
        "pregunta": "¿Cómo influye la cantidad de dormitorios en el precio?",
        "grafico": "grafico5",
        "analisis": [
            "Más dormitorios implica más precio, pero no de forma pareja: entre 1 y 2-3 dormitorios casi no hay diferencia (alrededor de 190 a 196 millones de CLP), el salto grande ocurre al pasar a 4-6 dormitorios (unos 371 millones), y de 4-6 a más de 6 el aumento es menor (unos 403 millones). Ten en cuenta que hay solo 24 propiedades de 1 dormitorio.",
            "Probablemente los dormitorios reflejan el tamaño general de la casa más que ser un factor independiente.",
        ],
    },
    6: {
        "titulo": "Precio según estacionamientos",
        "pregunta": "¿Cómo influye la presencia de estacionamiento en el precio final?",
        "grafico": "grafico6",
        "analisis": [
            "En algunos sectores, las propiedades con 5 o más estacionamientos llegan a casi el doble del precio de las que no tienen.” por “En varios sectores (Centro, Suroriente y Norte), las propiedades con 5 o más estacionamientos cuestan casi el doble o más que las que no tienen.",
            "En el sector Oriente el aumento es más moderado en términos relativos (de unos 586 a unos 746 millones entre “0” y “5+”), porque sus precios base ya son muy altos.",
            "La categoría “0” no sigue el patrón porque mezcla propiedades sin estacionamiento con propiedades donde el dato no fue reportado (los nulos se reemplazaron por 0). Además, más estacionamientos suelen ir de la mano con más dormitorios y más área.",
        ],
    },
    7: {
        "titulo": "Corredor por comuna y sector",
        "pregunta": "¿Influye la presencia de un corredor de propiedades en el precio final?",
        "grafico": "grafico7",
        "analisis": [
            "En la mayoría de los sectores las propiedades con corredor tienen un precio promedio distinto a las publicadas sin corredor, pero la magnitud y la dirección de la diferencia varían según sector y comuna. Por ejemplo, en Huechuraba las propiedades con corredor son más caras, mientras que en Colina ocurre lo contrario.",
            "Esto no implica que contratar un corredor suba el precio: es más probable que las propiedades de mayor valor sean las que con más frecuencia se publican a través de un corredor.",
        ],
    },
    8: {
        "titulo": "Corredor: comparación global",
        "pregunta": "¿Cuánto más caras son, en promedio, las propiedades con corredor?",
        "grafico": "grafico8",
        "analisis": [
            "Las propiedades con corredor tienen un precio promedio de 8.227 UF, un 33,2 % mayor que las publicadas sin corredor (6.177 UF).",
            "Limitación: el gráfico compara solo dos promedios globales y oculta la variación por sector, por lo que debe leerse junto con el gráfico anterior y no de forma aislada.",
        ],
    },
    9: {
        "titulo": "Precio por m² según comuna",
        "pregunta": "¿Cómo influye la comuna en el precio respecto al tamaño del área total?",
        "grafico": "grafico9",
        "analisis": [
            "Al dividir el precio por el área total se comparan comunas con terrenos de distinto tamaño. Las cinco comunas más caras por metro cuadrado son Vitacura, Providencia, Las Condes, Lo Barnechea y Ñuñoa, todas del sector Oriente; las más baratas rondan los 640 a 670 mil CLP por m² (El Monte, Tiltil, San José de Maipo, San Ramón y Melipilla).",
            "Si comparas este gráfico con el de precio por comuna y sector, puedes ver si el precio alto de una comuna se debe a su ubicación o simplemente a que sus propiedades son más grandes.",
        ],
    },
}


def fmt(valor, decimales=0):
    """Formato chileno: 1.234.567 o 1.234,5"""
    if pd.isna(valor):
        return "—"
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def tabla_informe(numero):
    """Devuelve (columnas, filas) con los datos de apoyo de cada informe."""
    df = df_limpio

    if numero == 1:
        variables = {"Price_UF": "Precio (UF)", "Dorms": "Dormitorios", "Baths": "Baños",
                     "Built Area": "Área construida (m²)", "Total Area": "Área total (m²)",
                     "Parking": "Estacionamientos"}
        filas = []
        for col, nombre in variables.items():
            s = df[col].astype(float)
            filas.append([nombre, fmt(s.mean(), 1), fmt(s.median(), 1), fmt(s.min(), 1),
                          fmt(s.max(), 1), fmt(s.skew(), 2)])
        return ["Variable", "Promedio", "Mediana", "Mínimo", "Máximo", "Asimetría"], filas

    if numero == 2:
        conteo = df["Comuna"].value_counts()
        pct = df["Comuna"].value_counts(normalize=True) * 100
        filas = [[c, fmt(conteo[c]), fmt(pct[c], 1) + " %"] for c in conteo.head(10).index]
        return ["Comuna", "Publicaciones", "Porcentaje"], filas

    if numero == 3:
        g = df.groupby("Sector")["Price_UF"].agg(["mean", "median", "count"])
        g = g.reindex([s for s in ORDEN_SECTORES if s in g.index])
        filas = [[s, fmt(r["mean"]), fmt(r["median"]), fmt(r["count"])] for s, r in g.iterrows()]
        return ["Sector", "Promedio (UF)", "Mediana (UF)", "Propiedades"], filas

    if numero == 4:
        prom = df.groupby("Comuna")["Price_UF"].mean().sort_values(ascending=False)
        filas = [["Más caras", c, fmt(v)] for c, v in prom.head(5).items()]
        filas += [["Más baratas", c, fmt(v)] for c, v in prom.tail(5).iloc[::-1].items()]
        return ["Grupo", "Comuna", "Precio promedio (UF)"], filas

    if numero == 5:
        g = df.groupby("Rango_Dorms", observed=True)["Price_CLP"].agg(["mean", "count"])
        filas = [[("1 dormitorio" if r == "1" else f"{r} dormitorios"), "$ " + fmt(v["mean"]), fmt(v["count"])]
                 for r, v in g.iterrows()]
        return ["Rango", "Precio promedio (CLP)", "Propiedades"], filas

    if numero == 6:
        orden = ["0", "1-2", "3-4", "5+"]
        t = (df.groupby(["Sector", "Rango_Parking"], observed=True)["Price_CLP"]
             .mean().unstack().reindex(columns=orden))
        t = t.reindex([s for s in ORDEN_SECTORES if s in t.index])
        filas = [[s] + [("$ " + fmt(v)) if pd.notna(v) else "—" for v in fila] for s, fila in t.iterrows()]
        return ["Sector"] + [f"{o} est." for o in orden], filas

    if numero == 7:
        t = df.groupby(["Sector", "Con_Corredor"])["Price_UF"].mean().unstack()
        t = t.reindex([s for s in ORDEN_SECTORES if s in t.index])
        filas = []
        for s, r in t.iterrows():
            dif = (r["Con Corredor"] / r["Sin Corredor"] - 1) * 100
            filas.append([s, fmt(r["Con Corredor"]), fmt(r["Sin Corredor"]), f"{dif:+.1f} %".replace(".", ",")])
        return ["Sector", "Con corredor (UF)", "Sin corredor (UF)", "Diferencia"], filas

    if numero == 8:
        g = df.groupby("Con_Corredor")["Price_UF"].agg(["mean", "count"])
        dif = (g.loc["Con Corredor", "mean"] / g.loc["Sin Corredor", "mean"] - 1) * 100
        filas = [[k, fmt(v["mean"]), fmt(v["count"])] for k, v in g.iterrows()]
        filas.append(["Diferencia", f"{dif:+.1f} %".replace(".", ","), ""])
        return ["Grupo", "Precio promedio (UF)", "Propiedades"], filas

    if numero == 9:
        prom = (df["Price_CLP"] / df["Total Area"]).groupby(df["Comuna"]).mean().sort_values(ascending=False)
        filas = [["Más caras", c, "$ " + fmt(v)] for c, v in prom.head(5).items()]
        filas += [["Más baratas", c, "$ " + fmt(v)] for c, v in prom.tail(5).iloc[::-1].items()]
        return ["Grupo", "Comuna", "Precio por m² (CLP)"], filas

    return [], []


def informe(request, numero):
    datos = INFORMES.get(numero)
    if datos is None:
        raise Http404("Informe no encontrado")
    columnas, filas = tabla_informe(numero)
    contexto = {"datos": datos, "columnas": columnas, "filas": filas}
    return render(request, "analisis/informe.html", contexto)
