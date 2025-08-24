#myapp/urls.py
from django.urls import path
from .views import map_view
from .views import registro, login_view


urlpatterns = [
    path('map/', map_view, name='map_view'), # /map/ ahora es la página principal del mapa
    path('map/registro/', registro, name='registro'),
    path('map/login/', login_view, name='login'),
]