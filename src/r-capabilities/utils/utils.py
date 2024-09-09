import yaml
import xarray as xr
import pandas as pd
import s3fs

def readConfiguration(propertie:str,value:str)->str:
    with open('conf/Cloud.yml','r') as file:
        ymlFile = yaml.safe_load(file)
    
    return ymlFile[propertie][value]

def initializeZarrConnection( s3Path: str
                             ,s3 
                             )->xr.Dataset:
    """
    Initializes a Zarr connection using an S3 path and S3 client.

    Parameters:
    - s3Path (str): The S3 path to the Zarr store.
    - s3: An S3 client object.

    Returns:
    - xarray.Dataset: The Zarr data as an xarray dataset.
    """
    zarrMap = s3fs.S3Map(root=s3Path, s3=s3, check=False)
    zarrData = xr.open_zarr(store=zarrMap, consolidated=True)
    return zarrData
    
def filterData(zarrData,rangeOfDates
               ,lat:float
               ,lon:float)->xr.Dataset:
    zarrData = zarrData.sel(time = rangeOfDates)
    zarrData = zarrData.sel(lat = lat,
                            lon = lon,
                            method = 'nearest'
                           )
    variables =  [i for i in zarrData.data_vars.keys()]
    if variables[0] == 'precipitation':
        zarrData = zarrData.where(zarrData[variables[0]]>=0)
    return zarrData

def filterArea(zarrData
               ,rangeOfDates
               ,xmax:float
               ,xmin:float
               ,ymax:float
               ,ymin:float
              )->xr.Dataset:
    zarrData = zarrData.sel(time = rangeOfDates)
    zarrData = zarrData.sel(lat=slice(ymax,ymin)
                            ,lon=slice(xmin, xmax)
                           )
    variables =  [i for i in zarrData.data_vars.keys()]
    if variables[0] == 'precipitation':
        zarrData = zarrData.where(zarrData[variables[0]]>=0)
    return zarrData


def filterAllArea(zarrData
               ,xmax:float
               ,xmin:float
               ,ymax:float
               ,ymin:float
              )->xr.Dataset:
    zarrData = zarrData.sel(lat=slice(ymax,ymin)
                            ,lon=slice(xmin, xmax)
                           )
    variables =  [i for i in zarrData.data_vars.keys()]
    if variables[0] == 'precipitation':
        zarrData = zarrData.where(zarrData[variables[0]]>=0)
    return zarrData