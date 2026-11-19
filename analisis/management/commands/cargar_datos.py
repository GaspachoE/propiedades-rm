"""
Carga el archivo data1.csv en la tabla Propiedad de la base de datos SQLite.

Uso:  python manage.py cargar_datos

Se ejecuta una sola vez, después de "python manage.py migrate". Si se vuelve a
ejecutar, borra las filas anteriores y las carga de nuevo (no quedan duplicados).
"""
from pathlib import Path

import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction

from analisis.models import COLUMNAS_CSV, Propiedad

RUTA_CSV = Path(__file__).resolve().parents[2] / "data" / "data1.csv"


class Command(BaseCommand):
    help = "Carga data1.csv en la tabla de propiedades de la base de datos"

    def handle(self, *args, **options):
        df = pd.read_csv(RUTA_CSV).rename(columns=COLUMNAS_CSV)
        # Las celdas vacías del CSV (NaN) se guardan como NULL en la base de datos
        df = df.astype(object).where(df.notna(), None)

        propiedades = [Propiedad(**fila) for fila in df.to_dict("records")]

        # transaction.atomic: si algo falla, no queda la tabla a medio cargar
        with transaction.atomic():
            Propiedad.objects.all().delete()
            Propiedad.objects.bulk_create(propiedades, batch_size=1000)

        self.stdout.write(self.style.SUCCESS(
            f"Se cargaron {Propiedad.objects.count()} propiedades en la base de datos."
        ))
