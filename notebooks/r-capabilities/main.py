#!/usr/bin/env python
# coding: utf-8

# In[1]:


import xarray as xr
import pandas as pd
import boto3
import numpy as np
import s3fs
import utils
from fastapi import FastAPI
from model.models import getDataRequest
from fastapi.responses import FileResponse
import random


# In[2]:


s3Key = utils.readConfiguration('read-access-keys','key')
s3Secret = utils.readConfiguration('read-access-keys','secret')
s3 = s3fs.S3FileSystem(key= s3Key
                       ,secret=s3Secret)

app = FastAPI(docs_url="/")
@app.post('/v1/getdataOnePoint')
async def getData(request: getDataRequest):
    s3Path = utils.readConfiguration('zarr-path',request.variableName)
    rangeOfDates = pd.date_range(start=request.startDt,end=request.endDt)
    zarrData = utils.initializeZarrConnection(s3Path,s3)
    zarrData = utils.filterData(zarrData,
                                rangeOfDates,
                                request.lat,
                                request.lon
                               )
    fileName = str(random.randint(0,250655))
    
    zarrData.to_netcdf(f'{fileName}.nc')
    return FileResponse(f'{fileName}.nc')
    
    
    



