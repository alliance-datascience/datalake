# install.packages('terra', repos='https://rspatial.r-universe.dev')
library(httr)
library(ncdf4)

install.packages('ncdf4')



url= 'https://zarr-query-api-rv7rkv4opa-uc.a.run.app/v1/getdataOnePoint'
query = '{
    "variableName": "agera5-maxairtemperature"
    ,"startDt":"2014-01-01"
    ,"endDt":"2014-02-01"
    ,"lat":2.8965 
    , "lon":-71.700696}'

POST(url, content_type_json(), body = query, write_disk("sampleR.nc", overwrite=TRUE))
zarrData <- ncdf4::nc_open("sampleR.nc")
attributes(zarrData$dim)
airTemperature = ncvar_get(zarrData
                   ,varid= "Temperature_Air_2m_Max_24h"
                   ,raw_datavals=TRUE )
time <- ncvar_get(zarrData, "time")

