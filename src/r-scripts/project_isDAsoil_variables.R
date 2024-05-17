options(warn = -1, scipen = 999)
suppressMessages(if(!require(pacman)){install.packages('pacman');library(pacman)} else {library(pacman)})
suppressMessages(pacman::p_load(terra))

## iSDAsoil dataset
# Test variable: pH
system.time(expr = {
  
  url <- 'https://isdasoil.s3.amazonaws.com/soil_data/ph/ph.tif'
  r <- terra::rast(paste0('/vsicurl/', url))
  
  ## Layers
  # pH, predicted mean at 0-20 cm depth
  # pH, predicted mean at 20-50 cm depth
  # pH, standard deviation at 0-20 cm depth
  # pH, standard deviation at 20-50 cm depth
  
  names(r) <- c('ph_avg_00-20cm', 'ph_avg_20-50cm', 'ph_std_00-20cm', 'ph_std_20-50cm')
  
  chirps_ref <- 'https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_daily/tifs/p05/2023/chirps-v2.0.2023.01.01.tif.gz'
  ref <- terra::rast(paste0('/vsigzip//vsicurl/',chirps_ref)); rm(chirps_ref)
  ref[ref == -9999] <- NA
  
  out_dir <- getwd()
  r_proj <- terra::project(x = r, y = ref, method = 'bilinear', threads = T)
  terra::writeRaster(x = r_proj, filename = paste0(out_dir,'/ph_0_05.tif'))
  terra::writeCDF(x = r_proj, filename = paste0(out_dir,'/ph_0_05.nc'),
                  varname = 'ph', longname = 'Soil pH',
                  unit = 'pH units times 10', compression = 9, overwrite = T)
  
})
