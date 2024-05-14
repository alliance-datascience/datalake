## ------------------------------------------ ##
## Create a 0.05 degrees resolution template
## covering full global extent
## By: Harold Achicanoy
## ABC, May 2024
## ------------------------------------------ ##

options(warn = -1, scipen = 999)
suppressMessages(if(!require(pacman)){install.packages('pacman');library(pacman)} else {library(pacman)})
suppressMessages(pacman::p_load(terra, ncdf4))

chirps_ref <- 'https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_daily/tifs/p05/2023/chirps-v2.0.2023.01.01.tif.gz'
ref <- terra::rast(paste0('/vsigzip//vsicurl/',chirps_ref)); rm(chirps_ref)
ref[ref == -9999] <- NA

fll <- terra::rast(terra::ext(-180, 180, -90, 90))
terra::crs(fll) <- terra::crs(ref)
terra::res(fll) <- terra::res(ref)
terra::origin(fll) <- terra::origin(ref)

terra::writeRaster(x = fll, filename = 'spatial_template_0_05_global.tif')
terra::writeCDF(x = fll, filename = 'spatial_template_0_05_global.nc',
                varname = 'template', longname = 'spatial template at 0.05 degrees resolution full extent',
                unit = 'none', compression = 9, overwrite = T)
