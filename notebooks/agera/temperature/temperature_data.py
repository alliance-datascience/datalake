#!/usr/bin/env python
# coding: utf-8

import xarray as xr
import pandas as pd
import numpy as np
import s3fs
import os
import re
import logging
from collections import defaultdict
import zarr
from numcodecs import blosc
from glob import glob
import dask
from dask import delayed, compute
from tqdm import tqdm
from dask.distributed import Client
from dask.diagnostics import ProgressBar
from datetime import datetime
import time

start_time = time.time()

# Configuración del logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("temperatura.log"),
                        logging.StreamHandler()
                    ])

logger = logging.getLogger(__name__)

# Función para transformar temperatura de kelvin a celsius

def kelvin_a_celsius(temp_k):
    return xr.where(np.isnan(temp_k), temp_k, temp_k - 273.15)

# Función para extraer fechas y tipos de los archivos .nc del directorio

def extraer_fecha_y_tipo(nombre_archivo):
    match = re.search(r'Temperature-Air-2m-(Max|Mean|Min)-24h.*_(\d{8})_', nombre_archivo)
    if match:
        tipo, fecha = match.groups()
        return fecha, tipo
    return '00000000', ''

# Función para construir dataframe de todos los archivos .nc del directorio ordenados

def archivos_mes(directorio):
    archivos = [f for f in os.listdir(directorio) if f.endswith('.nc')]
    data = []

    for archivo in archivos:
        fecha, tipo = extraer_fecha_y_tipo(archivo)
        if fecha != '00000000':
            data.append({
                'año': int(fecha[:4]),
                'mes': int(fecha[4:6]),
                'fecha': pd.to_datetime(fecha, format='%Y%m%d'),
                'tipo': tipo,
                'path': os.path.join(directorio, archivo)
            })

    df = pd.DataFrame(data)
    df.sort_values(by=['fecha', 'tipo'], inplace=True)
    df['tipo'] = pd.Categorical(df['tipo'], categories=['Max', 'Mean', 'Min'], ordered=True)
    df.sort_values(by=['fecha', 'tipo'], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

# Función para construir dataframe de todos los archivos .nc del directorio

def consolidate_nc(df_mes, año, mes):
    start_date = pd.Timestamp(f"{año}-{mes:02d}-01")
    end_date = start_date + pd.offsets.MonthEnd(0)
    datasets = xr.open_mfdataset(df_mes['path'].tolist(), chunks='auto', combine='by_coords') #, combine='by_coords', parallel=True
    # Convertir de Kelvin a Celsius
    for var_name in datasets.data_vars:
        datasets[var_name] = kelvin_a_celsius(datasets[var_name])
        datasets[var_name].attrs['units'] = 'C'
    return datasets

def append_zarr(año, mes, df_mes, bucket_salida, ruta_salida_s3):
    datasets = consolidate_nc(df_mes, año, mes)
    datasets = datasets.chunk({'time': 1, 'lat': 1801, 'lon': 3600}) # Ajuste de chunks antes de guardar en zarr
    s3 = s3fs.S3FileSystem(anon=False)
    zarr_store = s3fs.S3Map(root=f's3://{bucket_salida}/{ruta_salida_s3}', s3=s3)

    # Configurar compresión y encoding
    blosc.set_nthreads(8)
    compressor = zarr.Blosc(cname='lz4', clevel=1, shuffle=False)
    #encoding = {vname: {'compressor': compressor, 'chunks': (1, 1801, 3600)} for vname in datasets.data_vars}
    
    logger.info(f"Procesando año {año}, mes {mes}")
    with tqdm(total=100, desc=f"Procesando {año}-{mes:02d}") as pbar:
        try:
            datasets.to_zarr(zarr_store, mode='a', append_dim='time', consolidated=True, safe_chunks=False) # , safe_chunks=False
        except ValueError as e:
            # Si el archivo no existe, crear un nuevo archivo
            logger.warning(f"Error al abrir el archivo en modo append: {e}. Creando archivo nuevo.")
            datasets.to_zarr(zarr_store, mode='w', consolidated=True) # Eliminar , encoding=encoding
            logger.info(f"Nuevo archivo Zarr creado para el mes {año}-{mes:02d}")
        pbar.update(100)
    logger.info(f"Datos del mes {año}-{mes:02d} procesados y guardados en S3")

def procesar_rango_meses(fecha_inicio, fecha_fin, directorio, bucket_salida, ruta_salida_s3):
    # Convertir fechas de entrada a objetos datetime
    fecha_inicio = pd.to_datetime(fecha_inicio)
    fecha_fin = pd.to_datetime(fecha_fin)
    
    # Crear dataframe de todos los archivos a procesar
    df = archivos_mes(directorio)
    
    # Listar todos los meses en el rango de fechas
    rango_meses = pd.date_range(start=fecha_inicio, end=fecha_fin, freq='MS')
    
    # Configurar Dask Client
    client = Client(processes=True, n_workers=8, threads_per_worker=1, memory_limit='8GB')
    logger.info(f"Dask Client configurado: {client}")
    
    # Iterar sobre cada mes en el rango de meses a procesar
    for mes_actual in rango_meses:
        año = mes_actual.year
        mes = mes_actual.month

        # Filtrar archivos para el mes
        df_mes = df[(df['año'] == año) & (df['mes'] == mes)]
        append_zarr(año, mes, df_mes, bucket_salida, ruta_salida_s3)
        logger.info(f"Ejecutado mes: {año}/{mes}")
        
    client.close()
    logger.info("Proceso completado y Dask Client cerrado.")
    end_time = time.time()

    # Calcula el tiempo transcurrido
    elapsed_time = end_time - start_time
    print(f"Tiempo de procesamiento: {elapsed_time:.6f} segundos")
    logger.info(f"Tiempo de procesamiento: {elapsed_time:.6f} segundos")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Procesar archivos de temperatura')
    parser.add_argument('--directorio', type=str, required=True, help='Directorio con los archivos .nc')
    parser.add_argument('--fecha_inicio', type=str, required=True, help='Fecha de inicio en formato YYYY-MM-DD')
    parser.add_argument('--fecha_fin', type=str, required=True, help='Fecha de fin en formato YYYY-MM-DD')
    parser.add_argument('--bucket_salida', type=str, required=True, help='Bucket de salida en S3')
    parser.add_argument('--ruta_salida_s3', type=str, required=True, help='Ruta de salida en S3')
    
    args = parser.parse_args()

    procesar_rango_meses(args.fecha_inicio, args.fecha_fin, args.directorio, args.bucket_salida, args.ruta_salida_s3)

#nohup python temperature_data.py --directorio /home/ec2-user/SageMaker/datalake/data/agera/temperature/landing --fecha_inicio 1980-01-01 --fecha_fin 1980-12-31 --bucket_salida climate-action-datalake --ruta_salida_s3 zone=raw/source=agera5-v1-1/variable=temperatureAir.zarr &
