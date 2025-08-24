#myapp/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
import pandas as pd

# Create your models here.
class Project(models.Model):
    name = models.CharField(max_length=200)
      
class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE) # relacion con otra tabla (ForeignKey)

class RiesgoSiniestralidad(models.Model):
    ZONA_COLOR_CHOICES = [
        ('rojo', 'Alta Accidentalidad'),
        ('amarillo', 'Accidentalidad Media'),
        ('verde', 'Baja Accidentalidad'),
    ]

    zona = models.CharField(max_length=100)
    punto_interes = models.CharField(max_length=255)
    accidentes = models.IntegerField()
    coordenadas = models.JSONField()  # Para almacenar las coordenadas en formato JSON
    color = models.CharField(max_length=10, choices=ZONA_COLOR_CHOICES, default='verde')

    def __str__(self):
        return self.zona

    def asignar_color(self):
        """Método para asignar un color basado en el número de accidentes."""
        if self.accidentes > 10:
            self.color = 'rojo'
        elif 5 <= self.accidentes <= 10:
            self.color = 'amarillo'
        else:
            self.color = 'verde'
    def save(self, *args, **kwargs):
        self.asignar_color()  # Asigna el color antes de guardar
        super().save(*args, **kwargs)  # Llama al método save de la clase padre