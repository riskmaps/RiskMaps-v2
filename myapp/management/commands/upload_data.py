# myapp/management/commands/upload_data.py
import pandas as pd
import os
import json
import ast
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from myapp.models import RiesgoSiniestralidad
import numpy as np

class Command(BaseCommand):
    help = 'Limpia la tabla y carga datos desde todos los CSV en la carpeta Dato_riesgos'

    def handle(self, *args, **kwargs):
        # --- LIMPIA LA BASE DE DATOS ANTES DE CARGAR ---
        self.stdout.write(self.style.WARNING('Limpiando la base de datos de riesgos existentes...'))
        RiesgoSiniestralidad.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('¡Base de datos limpia!'))
        # --- FIN DE LA LIMPIEZA ---
        
        # 1. Definir la ruta a la carpeta de datos
        data_folder = Path(settings.BASE_DIR) / 'mysite' / 'dato_riesgos'

        # 2. Buscar todos los archivos CSV en esa carpeta
        csv_files = list(data_folder.glob('*.csv'))

        if not csv_files:
            self.stdout.write(self.style.WARNING('No se encontraron archivos CSV para cargar.'))
            return

        self.stdout.write(f"Se encontraron {len(csv_files)} archivos CSV para procesar.")

        # 3. Iterar sobre CADA archivo encontrado
        for csv_file_path in csv_files:
            self.stdout.write(self.style.HTTP_INFO(f"\n--- Procesando archivo: {csv_file_path.name} ---"))
            
            try:
                # Leer el archivo CSV actual
                df = pd.read_csv(csv_file_path)
                self.stdout.write(f"Archivo leído correctamente. {len(df)} filas encontradas.")
                
                # Reemplazar NaN en 'accidentes' con 0
                df['accidentes'] = df['accidentes'].fillna(0)
                
                # Contadores para seguimiento por archivo
                creados = 0
                actualizados = 0
                errores = 0

                # Iterar sobre las filas del DataFrame y guardar en la base de datos
                for index, row in df.iterrows():
                    try:
                        coord_str = row['coordenadas']
                        coordenadas = None

                        if pd.isna(coord_str):
                            coordenadas = []
                        elif isinstance(coord_str, str):
                            cleaned_str = coord_str.strip()
                            try:
                                coordenadas = ast.literal_eval(cleaned_str)
                            except (SyntaxError, ValueError):
                                try:
                                    coordenadas = json.loads(cleaned_str)
                                except json.JSONDecodeError:
                                    self.stderr.write(self.style.ERROR(f"Error al parsear coordenadas en fila {index}: {coord_str}"))
                                    errores += 1
                                    continue
                        else:
                            self.stderr.write(self.style.WARNING(f"Tipo inesperado en coordenadas fila {index}: {type(coord_str)}"))
                            errores += 1
                            continue

                        if coordenadas is not None:
                            obj, created = RiesgoSiniestralidad.objects.update_or_create(
                                zona=row['zona'],
                                punto_interes=row['punto_interes'],
                                defaults={
                                    'accidentes': int(row['accidentes']),
                                    'coordenadas': json.dumps(coordenadas, ensure_ascii=False)
                                }
                            )

                            if created:
                                creados += 1
                            else:
                                actualizados += 1

                    except Exception as e:
                        errores += 1
                        self.stderr.write(self.style.ERROR(f"Error al procesar fila {index}: {e}"))

                self.stdout.write(self.style.SUCCESS(
                    f"Archivo '{csv_file_path.name}' completado: {creados} creados, {actualizados} actualizados, {errores} errores."
                ))

            except FileNotFoundError:
                self.stderr.write(self.style.ERROR(f"El archivo no se encontró en: {csv_file_path}"))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error general al cargar '{csv_file_path.name}': {e}"))
