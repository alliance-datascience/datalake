import os
import shutil
from glob import glob
from datetime import datetime

def copiar_archivos_mes(ruta_origen, ruta_destino, año, mes):
    # Asegurarse de que la carpeta de destino exista
    os.makedirs(ruta_destino, exist_ok=True)

    # Patrón para los archivos del mes especificado
    patron = f"*_{año}{mes:02d}*_final-v1.1.nc"
    
    # Obtener la lista de archivos que coinciden con el patrón
    archivos = glob(os.path.join(ruta_origen, patron))

    # Copiar cada archivo a la carpeta de destino
    for archivo in archivos:
        nombre_archivo = os.path.basename(archivo)
        shutil.copy2(archivo, os.path.join(ruta_destino, nombre_archivo))
        print(f"Copiado: {nombre_archivo}")

    print(f"Se copiaron {len(archivos)} archivos a {ruta_destino}")

# Ejemplo de uso
ruta_origen = "datalake/data/agera/temperature/landing"
ruta_destino = "datalake/data/agera/temperature/tmp_test"
año = 1980
mes = 1  # Enero

# python datalake/src/population/pipeline/copy_files_nc.py

copiar_archivos_mes(ruta_origen, ruta_destino, año, mes)