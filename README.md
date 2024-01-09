
# WIP

## Repository content

> Data download
> Transform from tiff to NC
> Transform from NC to ZARR
> How to Zarr

## Source Data

| Datasource | Variable |
| ----------- | ----------- |
| CHIRP | Precipitation |
| CHIRT | Min temperature |
| AGERA5 | 10m Wind Speed|
| AGERA5 | 2m Relative humidity|
| AGERA5 | 2m Temperature |
| AGERA5 | Solar Flux |

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

