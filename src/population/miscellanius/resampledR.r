#install.packages('terra', repos='https://rspatial.r-universe.dev')
library('terra')
DATALAKE_CONF_PATH <- Sys.getenv("DATALAKE_CONF_PATH")
confFile = read_yaml(DATALAKE_CONF_PATH)
args = commandArgs(trailingOnly=TRUE)

confFile = confFile$args[1]
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

dataProcess = getFilesInFolder(confFile$pathforLanding)
newPath= confFile$pathforReggrid





for (i in seq(1,length(dataProcess))) {
  getName <- strsplit(dataProcess[i],"/")
  fileName = getName[[1]][length(getName[[1]])]
  print(paste("processing....",fileName))
  resampleRaster(rast_content=dataProcess[i]
                 , chirps=chirps
                 ,filename= paste0(newPath,fileName)
                 )
}


