
# datalake

This repository provides Python code for connecting to Amazon S3 and working with climate data using the xarray library. The data is stored in Zarr format on S3, and the code demonstrates how to access and manipulate climate data variables such as solar radiation flux, wind speed, relative humidity, and precipitation.

## Requirements
Python 3.x
xarray
s3fs
You can install the required libraries using the following command:

bash
Copy code
pip install xarray s3fs
## Usage
Clone this repository and use the provided Python script to connect to the specified S3 paths. Update the S3 paths in the script according to your data location.

python
Copy code
import xarray as xr

### Define S3 paths for different climate variables
s3ZarrPath = "s3://climate-action-datalake/zone=raw/source=agera5/variable=solarRadiationFlux.zarr/"
s3ZarrWindSpeed = "s3://climate-action-datalake/zone=raw/source=agera5/variable=windspeed.zarr/"
s3Humidity = "s3://climate-action-datalake/zone=raw/source=agera5/variable=relativehumidity.zarr/"
s3Precipitation = "s3://climate-action-datalake/zone=raw/source=chirps/variable=precipitation.zarr/"

### Define Store
storeWindSpeed = s3fs.S3Map(root=s3ZarrWindSpeed, s3=s3, check=False)
storeHumidity = s3fs.S3Map(root=s3Humidity, s3=s3, check=False)
storeSolarFlux = s3fs.S3Map(root=s3ZarrPath, s3=s3, check=False)
storePrecipitation = s3fs.S3Map(root=s3Precipitation, s3=s3, check=False)

