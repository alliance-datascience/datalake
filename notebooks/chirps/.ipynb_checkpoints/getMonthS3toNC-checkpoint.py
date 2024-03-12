#!/usr/bin/env python
# coding: utf-8

# In[1]:





# In[2]:


import os
import yaml
from datetime import datetime,timedelta
from yaml.loader import SafeLoader
import rioxarray as rx
import pandas as pd
import boto3
import xarray as xr
import glob
import shutil
import os
from dask.diagnostics import ProgressBar
from datetime import datetime
import numpy as np
from dask import dataframe as dd
import argparse
import logging
logging.basicConfig(format='%(asctime)s %(message)s')




ymlPath = 'conf/chirps.yml'





def readYamlConf(path: str):
    with open(path,'r') as conf:
        confArgs = yaml.load(conf, Loader= SafeLoader)
        #print(confArgs)
    return confArgs

def downloadDataFromS3FilteredByYear(s3Path: str
                                     , downloadPath: str
                                     , year:str 
                                     , month : str
                                    ):
    
    s3Command = f'aws s3 cp {s3Path} {downloadPath} --recursive --exclude "*" --include "chirps-v2.0.{year}.{month}.*"'
    #print(s3Command)
    return os.system(s3Command)

def uncompressGunzip (path:str):
    command = f'cd {path}| gunzip {path}*'
    os.system(command)
    

def VtransformCHIRTSToNc(inputPath, file, outputPath):
    tiffFile = inputPath+file
    allFiles = xr.open_dataset(tiffFile)
    dateContent = file.split('.')
    date = datetime(int(dateContent[-4]),int(dateContent[-3]),int(dateContent[-2]))
    filename = date.strftime('%Y%m%d')
    time_da = xr.DataArray({'time': date})
    allFiles = allFiles.assign_coords(time = date)
    allFiles = allFiles.expand_dims(dim="time")
    allFiles = allFiles.rename_vars(name_dict = {'band_data':'precipitation'})
    allFiles = allFiles.rename(name_dict   = {'x':'lon','y':'lat'})
    allFiles = allFiles.drop('band')
    allFiles = allFiles.drop('spatial_ref')
    allFiles.to_netcdf(f'{outputPath}{filename}.nc')
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser("Transforming tiff to NC")
    parser.add_argument("--execution_type")
    parser.add_argument("--year")
    parser.add_argument("--month")
    arguments = parser.parse_args()
    if arguments.execution_type in "manual":
        year = arguments.year
        month = arguments.month
    elif arguments.execution_type in "auto":
        twoMonthsDate = (datetime.now()-timedelta(days=60))
        year = twoMonthsDate.strftime('%Y')
        month = twoMonthsDate.strftime('%m')
    else:
        raise Exception("You must provide execution type")
    logging.info("Reading configuration file")
    confArgs = readYamlConf(ymlPath)
    chirpsArgs = confArgs['chirpsArguments']
    del confArgs
    logging.info("Downloading data")
    logCapture = downloadDataFromS3FilteredByYear(chirpsArgs['awsChirpsLandingPath']
                                     , chirpsArgs['pathforTGZ']
                                     ,year
                                     ,month
                                    )
    logging.info("Uncompressing gunzip files")
    uncompressGunzip(chirpsArgs['pathforTGZ'])
    tiffToTransform = os.listdir(chirpsArgs['pathforTGZ'])
    tiffToTransformDf = pd.DataFrame()
    tiffToTransformDf['files'] = tiffToTransform
    logging.info("Transform to NC")
    tiffToTransformDf.files.apply(lambda f: VtransformCHIRTSToNc(chirpsArgs['pathforTGZ']
                                                                , f
                                                                , chirpsArgs['pathforNCDF'])
                                )
    logging.info("Transform completed")