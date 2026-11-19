from django.db import models

# Columna del CSV original -> campo del modelo.
# Se usa al cargar el CSV en la base de datos (comando cargar_datos) y al
# leer la base de datos para volver a tener los nombres originales (CargaDatos.py).
COLUMNAS_CSV = {
    "Price_CLP": "price_clp",
    "Price_UF": "price_uf",
    "Price_USD": "price_usd",
    "Comuna": "comuna",
    "Ubicacion": "ubicacion",
    "Dorms": "dorms",
    "Baths": "baths",
    "Built Area": "built_area",
    "Total Area": "total_area",
    "Parking": "parking",
    "id": "id_publicacion",
    "Realtor": "realtor",
}


class Propiedad(models.Model):
    """Una publicación de venta de casa usada (una fila de data1.csv)."""

    price_clp = models.BigIntegerField("Precio (CLP)")
    price_uf = models.FloatField("Precio (UF)")
    price_usd = models.FloatField("Precio (USD)")
    comuna = models.CharField(max_length=60)
    ubicacion = models.CharField("Ubicación", max_length=200)
    # Estos campos pueden venir vacíos en el dataset original (null=True)
    dorms = models.FloatField("Dormitorios", null=True)
    baths = models.FloatField("Baños", null=True)
    built_area = models.FloatField("Área construida (m²)", null=True)
    total_area = models.FloatField("Área total (m²)", null=True)
    parking = models.FloatField("Estacionamientos", null=True)
    id_publicacion = models.BigIntegerField("ID de la publicación")
    realtor = models.CharField("Corredor", max_length=200, null=True)

    class Meta:
        verbose_name = "propiedad"
        verbose_name_plural = "propiedades"

    def __str__(self):
        return f"{self.comuna} - {self.price_uf:,.0f} UF"
