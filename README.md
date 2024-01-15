
# WIP

## Repository content

- Data download
- Transform from tiff to NC
- Transform from NC to ZARR
- How to Zarr

## Source Data

| Datasource | Variable |API Name|S3|
| ----------- | ----------- |----------- |----------- |
| CHIRP | Precipitation |chirps-precipitation |s3://climate-action-datalake/zone=raw/source=chirps/variable=precipitation.zarr/|
| CHIRT | Min temperature |WIP||
| AGERA5 | 10m Wind Speed|WIP||
| AGERA5 | 2m Relative humidity|WIP||
| AGERA5 | 2m Temperature Max |agera5-maxairtemperature|s3://climate-action-datalake/zone=raw/source=agera5/variable=airTemperatureMax.zarr/|
| AGERA5 | Solar Flux |agera5-solarflux|s3://climate-action-datalake/zone=raw/source=agera5/variable=solarRadiationFlux.zarr/|

## Requirements
- Python 3.x
- xarray
- s3fs
You can install the required libraries using the following command:
```
pip install xarray s3fs
```

## API
The API en endpoint for retraving data is: 
https://zarr-query-api-rv7rkv4opa-uc.a.run.app/v1/
### Method getdataOnePoint

This method return data for a variable and geopoint given:

The API supports the following query parameters:

- variableName: The variable name for the climate data. Example: "agera5-maxairtemperature"

- startDt: The start date for the data in the format "YYYY-MM-DD". Example: "2014-01-01"

- endDt: The end date for the data in the format "YYYY-MM-DD". Example: "2014-02-01"

- lat: The latitude of the specific point. Example: 2.8965

- lon: The longitude of the specific point. Example: -71.700696

The sample query in JSON format is:

```
{
    "variableName": "agera5-maxairtemperature",
    "startDt": "2014-01-01",
    "endDt": "2014-02-01",
    "lat": 2.8965,
    "lon": -71.700696
}
```

**In samples folder under R folder the file called zarrReading.r has an example of how to use the API**

## Usage
Clone this repository and use the provided Python script to connect to the specified S3 paths. Update the S3 paths in the script according to your data location.


python
Copy code
import xarray as xr

### Define S3 paths for different climate variables
```
s3ZarrPath = "s3://climate-action-datalake/zone=raw/source=agera5/variable=solarRadiationFlux.zarr/"
s3ZarrWindSpeed = "s3://climate-action-datalake/zone=raw/source=agera5/variable=windspeed.zarr/"
s3Humidity = "s3://climate-action-datalake/zone=raw/source=agera5/variable=relativehumidity.zarr/"
s3Precipitation = "s3://climate-action-datalake/zone=raw/source=chirps/variable=precipitation.zarr/"
```
### Define Store
```
storeWindSpeed = s3fs.S3Map(root=s3ZarrWindSpeed, s3=s3, check=False)
storeHumidity = s3fs.S3Map(root=s3Humidity, s3=s3, check=False)
storeSolarFlux = s3fs.S3Map(root=s3ZarrPath, s3=s3, check=False)
storePrecipitation = s3fs.S3Map(root=s3Precipitation, s3=s3, check=False)
```

