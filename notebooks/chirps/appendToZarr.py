#!/usr/bin/env python
# coding: utf-8

# In[1]:




# In[2]:


import xarray as xr
import s3fs
import boto3
import pandas as pd
from datetime import datetime
import yaml
from yaml import SafeLoader
import os
from numcodecs import blosc
import zarr
import logging
from dask.diagnostics import ProgressBar



logging.basicConfig(format='%(asctime)s %(message)s')
ymlPath = 'conf/chirps.yml'
s3 = s3fs.S3FileSystem()


def readYamlConf(path: str):
    with open(path,'r') as conf:
        confArgs = yaml.load(conf, Loader= SafeLoader)
        #print(confArgs)
    return confArgs



confArgs = readYamlConf(ymlPath)
chirpsArgs = confArgs['chirpsArguments']
del confArgs


chirpsS3 = s3fs.S3Map(root=chirpsArgs['awsChirpsRawPath'], s3=s3, check=False)


logging.warning("Loading files to append")
ncToLoad = os.listdir(chirpsArgs['pathforNCDF'])


for _nc in sorted(ncToLoad):
    _file = chirpsArgs['pathforNCDF']+_nc
    logging.warning("Opening %s ", _nc)
    nc = xr.open_dataset(_file)
    nc = nc[['time','band','lat','lon','precipitation']]
    logging.warning("Organizing dimensions")
    compressor = zarr.Blosc(cname='lz4', clevel= 1, shuffle=False)
    blosc.set_nthreads(8) 
    encoding = {vname: {'compressor': compressor,'chunks': (1,1,2000,7200)} for vname in nc.data_vars}
    with ProgressBar():
        nc.to_zarr(chirpsS3,  mode='a', append_dim='time', consolidated=True)
    logging.warning("Insert finished")


logging.warning("Process completed")
