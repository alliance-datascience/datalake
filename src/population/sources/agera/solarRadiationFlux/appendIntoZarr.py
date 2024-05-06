#!/usr/bin/env python
# coding: utf-8


import pandas as pd
import boto3
import xarray as xr
import os
import zarr
import s3fs
from dask.diagnostics import ProgressBar
from datetime import datetime
from yaml import safe_load
from numcodecs import blosc
import logging
logging.basicConfig(format='%(asctime)s %(message)s')




class appendIntoZarr:



    def convertRadiation(self,
                         k):
        c = k/1000000
        return c

    def netcdfChange(self
                     ,path
                     , file
                     , variableName: str):
        dt = file.split('_')[-2]
        dt = datetime.strptime(dt,
                               '%Y%m%d')
        f = xr.open_dataset(path+file)
        f = f.drop_vars(['crs'])
        f = f.rename_vars(name_dict = {'Band1':variableName})
        #time_da = xr.DataArray({'time': dt})
        f = f.assign_coords(time = dt)
        f = f.expand_dims(dim="time")
        return f



    def loadData(self,
                 ncToLoad:[],
                confFile,
                ageraS3):
        for _nc in sorted(ncToLoad):
            varName = "Solar-Radiation-Flux"
            logging.warning("Opening %s ", _nc)
            nc = self.netcdfChange(confFile['pathforReggrid'],
                              _nc,
                              varName)
            nc = nc.apply(self.convertRadiation)
            nc = nc[['time',
                     'lat',
                     'lon',
                     varName]]
            logging.warning("Organizing dimensions")
            compressor = zarr.Blosc(cname='lz4',
                                    clevel=1,
                                    shuffle=False)
            blosc.set_nthreads(8)
            encoding = {vname:{'compressor':compressor,
                                'chunks':(1,
                                           1,
                                           2000,
                                           7200)} for vname in nc.data_vars}
            with ProgressBar():
                print("Hello")
                #nc.to_zarr(ageraS3,  mode='a-', append_dim='time', consolidated=True)
            logging.warning("Insert finished")

    def __init__(self):
        s3 = s3fs.S3FileSystem()
        confType = 'agera5ArgumentsSolarFlux'
        ymlPath = os.environ["DATALAKE_CONF_PATH"]
        conf_args = safe_load(open(ymlPath, 'r'))  # Use safe_load for security
        confFile = conf_args[confType]
        ageraS3 = s3fs.S3Map(root=confFile['s3Raw'],
                             s3=s3,
                             check=False)
        logging.warning("Loading files to append")
        ncToLoad = os.listdir(
            confFile['pathforReggrid'])
        self.loadData(ncToLoad,
                      confFile,
                      ageraS3)
        logging.warning("Process completed")






