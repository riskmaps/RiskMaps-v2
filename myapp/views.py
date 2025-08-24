# myapp/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login 
from django.contrib.auth import login  
from django.conf import settings
from .forms import RegistroForm
from .models import RiesgoSiniestralidad
import json
import pandas as pd
from django.contrib import messages


def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        print(f"DATOS RECIBIDOS: {form.data}")  
        if form.is_valid():
            user = form.save() # Guarda el nuevo usuario
            # Puedes loguear al usuario aquí si lo deseas
            login(request, user) # Iniciar sesión automáticamente después del registro                
            messages.success(request, '¡Registro exitoso!')
            return redirect('map_view')  # Redirige a la página deseada
        else:
            return render(request, 'myapp/registro.html', {'form': form})

    else:
        form = RegistroForm()
    return render(request, 'myapp/registro.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('map_view') 
        else:
            form.add_error(None, 'Nombre de usuario o contraseña incorrectos.')  # Añadir error
        return render(request, 'myapp/login.html', {'form': form})  # Renderizar con el formulario (con o sin errores)form = AuthenticationForm()
    else:
        form = AuthenticationForm()
    return render(request, 'myapp/login.html', {'form': form})


#@login_required
def map_view(request):
    google_maps_api_key = settings.GOOGLE_MAPS_API_KEY
    # Lógica para obtener los datos del mapa (riskData)
    risk_data = RiesgoSiniestralidad.objects.all().values('zona', 'punto_interes','accidentes', 'coordenadas')

    # Convertir QuerySet a lista
    risk_list = list(risk_data)

    # Convertir la lista a JSON para usar en JavaScript
    risk_json = json.dumps(risk_list, ensure_ascii=False)
    
    context = {
        'google_maps_api_key': google_maps_api_key,
        'riskData': risk_json  # Pasamos SOLO el JSON al template
    }

    return render(request, 'myapp/map.html', context)
