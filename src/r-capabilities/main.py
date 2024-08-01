

import xarray as xr
import pandas as pd
import boto3
import numpy as np
import s3fs
from utils import utils
from fastapi import FastAPI
from model.models import getDataRequest,getDataRequestArea,getDataRequestAll
from fastapi.responses import FileResponse
import random
import os





s3Key = os.environ["KEY"]
s3Secret = os.environ["SECRET"]

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
    
    zarr_response = zarrData.to_dataframe()
    return zarr_response.to_json(orient='records')


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
                                ,request.xmax
                                ,request.xmin
                                ,request.ymax
                                ,request.ymin
                               )
    fileName = str(random.randint(0,250655))
    
    zarrData.to_netcdf(f'{fileName}.nc')
    return FileResponse(f'{fileName}.nc')

@app.post('/v1/getAllData')
def getAllData(request: getDataRequestAll):
    global s3
    print("S3 Key :", request.variableName)
    
    s3Path = utils.readConfiguration('zarr-path',request.variableName)
    #rangeOfDates = pd.date_range(start=request.startDt,end=request.endDt)
    print("S3 Key :", s3Path, "---- ")
    zarrData = utils.initializeZarrConnection(s3Path,s3)
    zarrData = utils.filterAllArea(zarrData
                                ,request.xmax
                                ,request.xmin
                                ,request.ymax
                                ,request.ymin
                               )
    fileName = str(random.randint(0,250655))
    
    zarrData.to_netcdf(f'{fileName}.nc')
    return FileResponse(f'{fileName}.nc')
    
    
    



