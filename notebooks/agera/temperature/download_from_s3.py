#!/usr/bin/env python
# coding: utf-8

import boto3
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configurar el cliente de S3
s3 = boto3.client('s3')

# Configurar las rutas
bucket_name = 'climate-action-datalake'
s3_prefix = 'zone=landing/source=agera5-v1-1/variable=2m_temperature/'
local_dir = '/home/ec2-user/SageMaker/datalake/data/agera/temperature/landing'

# Asegurarse de que el directorio local existe
os.makedirs(local_dir, exist_ok=True)

# Función para descargar un archivo individual
def download_file(obj):
    local_file_path = os.path.join(local_dir, obj['Key'][len(s3_prefix):])
    os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
    s3.download_file(bucket_name, obj['Key'], local_file_path)
    return obj['Key'], obj['Size']

# Función principal
def main():
    start_time = time.time()
    total_size = 0
    file_count = 0

    # Listar todos los objetos en el prefijo
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket_name, Prefix=s3_prefix)

    # Usar ThreadPoolExecutor para descargas paralelas
    with ThreadPoolExecutor(max_workers=16) as executor:
        future_to_file = {}
        for page in pages:
            for obj in page.get('Contents', []):
                future = executor.submit(download_file, obj)
                future_to_file[future] = obj['Key']

        for future in as_completed(future_to_file):
            file_key, file_size = future.result()
            total_size += file_size
            file_count += 1
            print(f"Descargado: {file_key}")

    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\nDescarga completada.")
    print(f"Tiempo total: {duration:.2f} segundos")
    print(f"Archivos descargados: {file_count}")
    print(f"Tamaño total descargado: {total_size / (1024*1024*1024):.2f} GB")

if __name__ == "__main__":
    main()