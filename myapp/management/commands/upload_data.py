# myapp/management/commands/upload_data.py
import pandas as pd
import os
import json
import ast
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from myapp.models import RiesgoSiniestralidad
import numpy as np  # Importa numpy para manejar NaN

class Command(BaseCommand):
    help = 'Carga datos desde un archivo CSV a la base de datos'

    def handle(self, *args, **kwargs):
        # Configura la ruta al archivo CSV
        data_folder = Path(settings.BASE_DIR) / 'mysite' / 'Dato_riesgos'
        csv_file_path = data_folder / 'datos_riesgo.csv'

        # Imprimir la ruta del archivo CSV
        self.stdout.write(f"Ruta del archivo CSV: {csv_file_path}")

        try:
            # Leer el archivo CSV
            df = pd.read_csv(csv_file_path)
            self.stdout.write(f"Archivo CSV leído correctamente. {len(df)} filas encontradas.")
            df['accidentes'] = df['accidentes'].fillna(0)
            # Contador para seguimiento
            creados = 0
            actualizados = 0
            errores = 0

            # Iterar sobre las filas del DataFrame y guardar en la base de datos
            for index, row in df.iterrows():
                try:
                    # Obtener el valor de la columna 'coordenadas'
                    coord_str = row['coordenadas']
                    print(f"Tipo de coordenadas para la fila {index}: {type(coord_str)}, Valor: {coord_str}")
                    coordenadas = None

                    # Manejar valores NaN
                    if pd.isna(coord_str):
                        coordenadas = []  # O None, o lo que desees para datos faltantes
                    elif isinstance(coord_str, str):
                        # Limpiar la cadena y convertirla
                        cleaned_str = coord_str.strip().replace('"', '').replace("'", "")
                        try:
                            coordenadas = ast.literal_eval(cleaned_str)
                        except (SyntaxError, ValueError):
                            try:
                                coordenadas = json.loads(cleaned_str)
                            except (json.JSONDecodeError):
                                self.stderr.write(self.style.ERROR(f"Error al parsear coordenadas en fila {index}: {coord_str}"))
                                errores += 1
                                continue # Saltar a la siguiente fila si no se puede parsear
                    else:
                        # Si no es str ni NaN, podría ser un tipo inesperado
                        self.stderr.write(self.style.WARNING(f"Tipo inesperado en coordenadas fila {index}: {type(coord_str)}, Valor: {coord_str}"))
                        errores += 1
                        continue # Saltar a la siguiente fila

                    if coordenadas is not None:
                        # Usar update_or_create para evitar duplicados
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
                            self.stdout.write(f"Creada nueva zona: {obj.zona}")
                        else:
                            actualizados += 1
                            self.stdout.write(f"Actualizada zona existente: {obj.zona}")

                except Exception as e:
                    errores += 1
                    self.stderr.write(self.style.ERROR(f"Error general al procesar fila {index}: {e}"))

            self.stdout.write(self.style.SUCCESS(
                f"Proceso completado: {creados} zonas creadas, {actualizados} actualizados, {errores} errores."
            ))

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"El archivo CSV no se encontró en: {csv_file_path}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Ocurrió un error general durante la carga: {e}"))