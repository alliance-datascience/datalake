

import xarray as xr
import pandas as pd
import boto3
import numpy as np
import s3fs
from utils import utils
from fastapi import FastAPI
from model.models import getDataRequest,getDataRequestArea
from fastapi.responses import FileResponse
import random





s3Key = utils.readConfiguration('read-access-keys','key')
s3Secret = utils.readConfiguration('read-access-keys','secret')

s3 = s3fs.S3FileSystem(key= s3Key
                       ,secret=s3Secret)

app = FastAPI(docs_url="/")
@app.post('/v1/getdataOnePoint')
def getData(request: getDataRequest):
    global s3
    print("S3 Key :", request.variableName)
    
    s3Path = utils.readConfiguration('zarr-path',request.variableName)
    rangeOfDates = pd.date_range(start=request.startDt,end=request.endDt)
    print("S3 Key :", s3Path, "---- ")
    zarrData = utils.initializeZarrConnection(s3Path,s3)
    zarrData = utils.filterData(zarrData,
                                rangeOfDates,
                                request.lat,
                                request.lon
                               )
    fileName = str(random.randint(0,250655))
    
    zarrData.to_netcdf(f'{fileName}.nc')
    return FileResponse(f'{fileName}.nc')


@app.post('/v1/getdataArea')
def getDataArea(request: getDataRequestArea):
    global s3
    print("S3 Key :", request.variableName)
    
    s3Path = utils.readConfiguration('zarr-path',request.variableName)
    rangeOfDates = pd.date_range(start=request.startDt,end=request.endDt)
    print("S3 Key :", s3Path, "---- ")
    zarrData = utils.initializeZarrConnection(s3Path,s3)
    zarrData = utils.filterArea(zarrData
                                ,rangeOfDates
                                ,request.xmax:float
                                ,request.xmin:float
                                ,request.ymax:float
                                ,request.ymin:float
                               )
    fileName = str(random.randint(0,250655))
    
    zarrData.to_netcdf(f'{fileName}.nc')
    return FileResponse(f'{fileName}.nc')
    
    
    



