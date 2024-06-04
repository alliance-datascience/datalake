options(warn = -1, scipen = 999)
suppressMessages(if(!require(pacman)){install.packages('pacman');library(pacman)} else {library(pacman)})
suppressMessages(pacman::p_load(terra, ncdf4))

reProject <- function(url, lyr_names, var_name, long_name, var_units, outfile){
  
  # Read original raster
  r <- terra::rast(paste0('/vsicurl/', url))
  names(r) <- lyr_names
  
  # Reference raster (CHIRPS)
  chirps_ref <- 'https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_daily/tifs/p05/2023/chirps-v2.0.2023.01.01.tif.gz'
  ref <- terra::rast(paste0('/vsigzip//vsicurl/',chirps_ref)); rm(chirps_ref)
  ref[ref == -9999] <- NA
  
  r_proj <- terra::project(x = r, y = ref, method = 'bilinear', threads = T, filename = paste0(outfile,'.tif'), overwrite = T)
  terra::writeCDF(x = r_proj, filename = paste0(outfile,'.nc'), varname = var_name, longname = long_name, unit = var_units, compression = 9, overwrite = T)
  
  return('Done!\n')
  
}

# url <- 'https://isdasoil.s3.amazonaws.com/soil_data/aluminium_extractable/aluminium_extractable.tif'
# lyr_names <- c('aluminium_avg_00-20cm', 'aluminium_avg_20-50cm', 'aluminium_std_00-20cm', 'aluminium_std_20-50cm')
# var_name  <- 'aluminium_extractable'
# long_name <- 'Aluminium extractable'
# var_units <- 'ppm'
# outfile   <- paste0('//CATALOGUE/WFP_ClimateRiskPr1/agroclimExtremes/',gsub('.tif','',basename(url)))
# reProject(url, lyr_names, var_name, long_name, var_units, outfile)

# url <- 'https://isdasoil.s3.amazonaws.com/soil_data/bedrock_depth/bedrock_depth.tif'
# lyr_names <- c('bedrock_avg_00-200cm', 'bedrock_std_00-200cm')
# var_name  <- 'bedrock_depth'
# long_name <- 'Depth to bedrock'
# var_units <- 'cm'
# outfile   <- paste0('//CATALOGUE/WFP_ClimateRiskPr1/agroclimExtremes/',gsub('.tif','',basename(url)))
# reProject(url, lyr_names, var_name, long_name, var_units, outfile)

# url <- 'https://isdasoil.s3.amazonaws.com/soil_data/bulk_density/bulk_density.tif'
# lyr_names <- c('bulk_avg_00-20cm', 'bulk_avg_20-50cm', 'bulk_std_00-20cm', 'bulk_std_20-50cm')
# var_name  <- 'bulk_density'
# long_name <- 'Bulk density, <2mm fraction'
# var_units <- 'g/cc'
# outfile   <- paste0('//CATALOGUE/WFP_ClimateRiskPr1/agroclimExtremes/',gsub('.tif','',basename(url)))
# reProject(url, lyr_names, var_name, long_name, var_units, outfile)

url <- 'https://isdasoil.s3.amazonaws.com/soil_data/calcium_extractable/calcium_extractable.tif'
lyr_names <- c('calcium_avg_00-20cm', 'calcium_avg_20-50cm', 'calcium_std_00-20cm', 'calcium_std_20-50cm')
var_name  <- 'calcium_extractable'
long_name <- 'Calcium extractable'
var_units <- 'ppm'
outfile   <- paste0('//CATALOGUE/WFP_ClimateRiskPr1/agroclimExtremes/',gsub('.tif','',basename(url)))
reProject(url, lyr_names, var_name, long_name, var_units, outfile)

# ## iSDAsoil dataset
# # Test variable: pH
# system.time(expr = {
#   
#   url <- 'https://isdasoil.s3.amazonaws.com/soil_data/ph/ph.tif'
#   r <- terra::rast(paste0('/vsicurl/', url))
#   
#   ## Layers
#   # pH, predicted mean at 0-20 cm depth
#   # pH, predicted mean at 20-50 cm depth
#   # pH, standard deviation at 0-20 cm depth
#   # pH, standard deviation at 20-50 cm depth
#   
#   names(r) <- c('ph_avg_00-20cm', 'ph_avg_20-50cm', 'ph_std_00-20cm', 'ph_std_20-50cm')
#   
#   chirps_ref <- 'https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_daily/tifs/p05/2023/chirps-v2.0.2023.01.01.tif.gz'
#   ref <- terra::rast(paste0('/vsigzip//vsicurl/',chirps_ref)); rm(chirps_ref)
#   ref[ref == -9999] <- NA
#   
#   memory.limit()
#   memory.limit(size = 15000)
#   
#   out_dir <- getwd()
#   r_proj <- terra::project(x = r, y = ref, method = 'bilinear', threads = T, filename = paste0(out_dir,'/ph_0_05.tif'), overwrite = T)
#   terra::writeCDF(x = r_proj, filename = paste0(out_dir,'/ph_0_05.nc'),
#                   varname = 'ph', longname = 'Soil pH',
#                   unit = 'pH units times 10', compression = 9, overwrite = T)
#   
# })
