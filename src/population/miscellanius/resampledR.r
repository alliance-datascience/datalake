#install.packages('terra', repos='https://rspatial.r-universe.dev')
library('terra')

chirps <- rast('data/20230101.nc')

resampleRaster <- function(rast_content, chirps, method = 'bilinear'
                          , threads = TRUE, filename, overwrite = TRUE) {
  # Load rast content
  originalData <- rast(rast_content)
  resample(originalData, chirps, method = method
           , threads = threads, filename = filename
           , overwrite = overwrite)

}


getFilesInFolder <- function(folderPath) {
  files <- list.files(path = folderPath, full.names = TRUE)
  return(files)
}

dataProcess = getFilesInFolder('/home/ruser/data/netcdf')
newPath= '/home/ruser/data/resampled/'





for (i in seq(11446,length(dataProcess))) {
  getName <- strsplit(dataProcess[i],"/")
  fileName = getName[[1]][length(getName[[1]])]
  print(paste("processing....",fileName))
  resampleRaster(rast_content=dataProcess[i]
                 , chirps=chirps
                 ,filename= paste0(newPath,fileName)
                 )
}


idx <- which(dataProcess  == "/home/ruser/data/netcdf/Solar-Radiation-Flux_C3S-glob-agric_AgERA5_20110503_final-v1.0.nc") 



dataProcess
