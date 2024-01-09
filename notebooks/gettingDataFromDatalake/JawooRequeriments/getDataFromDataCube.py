# %%
# Importing the needed libraries

import xarray as xr
import pandas as pd
import boto3
import numpy as np
import s3fs
from dask import dataframe as dd
from dask.diagnostics import ProgressBar

# %%

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

def locationDataframe(zarrData,lat,lon) -> pd.DataFrame:
    """
    Extracts location-based data from a Zarr dataset and returns it as a Pandas DataFrame.

    Parameters:
    - zarrData (xarray.Dataset): The Zarr dataset containing spatial data.
    - lat (float): Latitude value for the desired location.
    - lon (float): Longitude value for the desired location.

    Returns:
    - pandas.DataFrame: A DataFrame containing the extracted data for the specified location.
    """
    zarrData = zarrData.sel(lat = lat
                            , lon = lon
                            , method='nearest')
    df = zarrData.to_dataframe().reset_index()
    df['lat'] = lat
    df['lon'] = lon
    return df

def generateCSVLocationVariables(lat: float
                                 ,lon: float
                                 ,outputPath:str = None
                                 ):
    """
    Generates a CSV file containing climate variables for a specific location (latitude, longitude).

    Parameters:
    - lat (float): Latitude value for the desired location.
    - lon (float): Longitude value for the desired location.
    - outputPath (str, optional): Path to the directory where the CSV file will be saved. If not provided,
      the CSV file will be saved in the current working directory.

    Example:
    ```python
    generateCSVLocationVariables(lat=35.0, lon=-120.0, outputPath='/path/to/output/')
    ```

    Note:
    - The function utilizes the `initializeZarrConnection` and `locationDataframe` functions to extract
      climate data for the specified location from Zarr datasets.
    - The resulting CSV file includes columns for time, Julian day ('@DATE'), maximum temperature ('TMAX'),
      minimum temperature ('TMIN'), and precipitation ('RAIN').
    - The CSV file is saved with a ';' delimiter and rounded to one decimal place.
    """
    _lat = lat
    _lon = lon
    global rangeOfDates
    tmaxData = initializeZarrConnection(agera5Tmax,s3)
    tminData = initializeZarrConnection(agera5Tmin,s3)
    prepData = initializeZarrConnection(chirpsPrecipitation,s3)
    tmaxData = tmaxData.sel( time = rangeOfDates )
    tminData = tminData.sel( time = rangeOfDates )
    prepData = prepData.sel( time = rangeOfDates )
    df1 = locationDataframe(tmaxData,_lat,_lon )
    df2 = locationDataframe(tminData,_lat,_lon )
    df3 = locationDataframe(prepData,_lat,_lon )
    df1['j_day'] = df1.time.apply(lambda x: x.strftime('%y') +x.strftime('%j') )
    alldf = df1.join(df2.set_index(['time','lat','lon']), on = ['time','lat','lon'])
    alldf = alldf.join(df3.set_index(['time','lat','lon']), on = ['time','lat','lon'])
    alldf = alldf[['time','j_day','Temperature_Air_2m_Min_24h','Temperature_Air_2m_Max_24h','precipitation']]
    alldf = alldf.rename(columns={'j_day':'@DATE'
                ,'Temperature_Air_2m_Max_24h': 'TMAX'
                ,'Temperature_Air_2m_Min_24h': 'TMIN'
                ,'precipitation':'RAIN'})

    alldf = alldf.round(decimals=1)
    if outputPath:
        alldf.to_csv(outputPath+'data_'+str(_lat)+"_"+str(lon)+'.csv',sep=';')
    else:
        alldf.to_csv('data_'+str(_lat)+"_"+str(lon)+'.csv',sep=';')



# %%
# Define location files
pathOfLocationFile = 'location.csv'
# Define paths for Zarr datasets
agera5Tmax = "s3://climate-action-datalake/zone=raw/source=agera5/variable=airTemperatureMax.zarr/"
agera5Tmin = "s3://climate-action-datalake/zone=raw/source=agera5/variable=airTemperatureMin.zarr/"
chirpsPrecipitation = "s3://climate-action-datalake/zone=raw/source=chirps/variable=precipitation.zarr/"
# Define date range
startDt = '2010-01-01'
endDt = '2010-01-31'
# S3 credentials
s3Key = 'AKIATHPVGK3ZVLVSHEEF'
s3Secret = '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'
# Generate date range
rangeOfDates = pd.date_range(start=startDt,end=endDt)
# Initialize S3FileSystem object
s3 = s3fs.S3FileSystem(key = s3Key
                       ,secret = s3Secret)
# Read location data from CSV file
locationDf = pd.read_csv(pathOfLocationFile,sep=';')
# Extract column names from the location DataFrame
colDfNames = locationDf.columns
# Set the number of partitions for Dask DataFrame
npartitions = 10
# Create a Dask DataFrame from the location DataFrame
locationDD = dd.from_pandas(locationDf,npartitions=npartitions)


# %%
progess = ProgressBar()  
with progess:
    # Use map_partitions to apply the generateCSVLocationVariables function to each partition for generating CSV file
    locationDD.map_partitions(lambda 
                              df: df.apply(lambda loc: generateCSVLocationVariables(loc[colDfNames[0]],
                                                          loc[colDfNames[1]]),axis = 1 )).compute(scheduler='processes')


