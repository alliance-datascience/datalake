### Datalake use
## Data retrieval
# Arguments: startDate, endDate
#            xmin, xmax, ymin, ymax
#            variable
#            downloadpath
python_command <- "python getDataFromCubeZone.py --startDate='05-11' --endDate='08-30' --xmin=-90 --xmax=-83 --ymin=12 --ymax=16 --variable='chirps-precipitation' --downloadpath='/tmp/'"
system(python_command)
# Results: .nc files downloaded in downloadpath
## Load files in R using terra library
fls <- list.files(path = '/tmp/', pattern = '*.nc$', full.names = T)
r <- terra::rast(fls[1])