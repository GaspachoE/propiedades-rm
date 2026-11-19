from django.contrib import admin

from .models import Propiedad


# Permite revisar la tabla de propiedades desde /admin
@admin.register(Propiedad)
class PropiedadAdmin(admin.ModelAdmin):
    list_display = ("comuna", "price_uf", "dorms", "baths", "total_area", "realtor")
    list_filter = ("comuna",)
    search_fields = ("comuna", "ubicacion", "realtor")
