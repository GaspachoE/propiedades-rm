from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="grafico1"), name="index"),
    path("grafico1", views.grafico1, name="grafico1"),
    path("grafico2", views.grafico2, name="grafico2"),
    path("grafico3", views.grafico3, name="grafico3"),
    path("mapa", views.grafico4, name="grafico4"),
    path("grafico5", views.grafico5, name="grafico5"),
    path("grafico6", views.grafico6, name="grafico6"),
    path("grafico7", views.grafico7, name="grafico7"),
    path("grafico8", views.grafico8, name="grafico8"),
    path("grafico9", views.grafico9, name="grafico9"),
    path("informe/<int:numero>", views.informe, name="informe"),
]