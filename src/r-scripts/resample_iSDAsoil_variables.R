# ------------------------------------------ #
# Resampling iSDAsoil dataset
# By: Harold Achicanoy
# Alliance Bioversity CIAT
# June 2024
# ------------------------------------------ #

## R options and packages loading ----
options(warn = -1, scipen = 999)
suppressMessages(if(!require(pacman)){install.packages('pacman');library(pacman)} else {library(pacman)})
suppressMessages(pacman::p_load(terra, ncdf4, readxl, gdalUtilities))

src_dir <- 'D:/ToBackup/CGIAR_climate_action/datalake'

## Setup table ----
stp <- readxl::read_excel(path = paste0(src_dir,'/data/soils_metadata.xlsx'), sheet = 3) |> base::as.data.frame()

u <- stp$URL[1]
u <- paste0('/vsicurl/',u)

# r <- terra::rast(u)

# Temporal vrt rasters
intrmd_vrt <- paste0(tempfile(),'.vrt') # Intermediate raster
output_vrt <- paste0(tempfile(),'.vrt') # Final raster

## GDAL operations
# gdalbuildvrt -b 1 -resolution highest -r nearest "output.vrt" "input.tif"
# gdalwarp -t_srs EPSG:4326 output.vrt output_warped.vrt

# Resample to 5x5km
gdalUtilities::gdalbuildvrt(gdalfile = u, output.vrt = intrmd_vrt, b = 1, resolution = 'user', tr = c(5500, 5500), r = 'bilinear')
# Original CRS to EPSG:4326
gdalUtilities::gdalwarp(srcfile = intrmd_vrt, dstfile = output_vrt, t_srs = 'EPSG:4326')

outdir <- '//CATALOGUE/WFP_ClimateRiskPr1/agroclimExtremes/iSDA'

# Load GDAL vrt result
r <- terra::rast(output_vrt)
# Write GDA: vrt result to tif
terra::writeRaster(x = r, filename = paste0(outdir,'/',gsub('.tif','',basename(u)),'_intrmd.tif'), overwrite = T)
r <- terra::rast(paste0(outdir,'/',gsub('.tif','',basename(u)),'_intrmd.tif'))

# Reference raster (CHIRPS)
chirps_ref <- 'https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_daily/tifs/p05/2023/chirps-v2.0.2023.01.01.tif.gz'
ref <- terra::rast(paste0('/vsigzip//vsicurl/',chirps_ref)); rm(chirps_ref)
ref[ref == -9999] <- NA

# Save resampled raster into tif and nc formats
r_rsmp <- terra::resample(x = r, y = ref, method = 'bilinear', threads = T, filename = paste0(outdir,'/',gsub('.vrt','.tif',basename(u))), overwrite = T)
terra::writeCDF(x = r_rsmp, filename = paste0(outdir,'/',gsub('.tif','.nc',basename(u))), varname = var_name, longname = long_name, unit = var_units, compression = 9)



# Read original raster
r <- terra::rast(paste0('/vsicurl/', url))
names(r) <- lyr_names

# Reference raster (CHIRPS)
chirps_ref <- 'https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_daily/tifs/p05/2023/chirps-v2.0.2023.01.01.tif.gz'
ref <- terra::rast(paste0('/vsigzip//vsicurl/',chirps_ref)); rm(chirps_ref)
ref[ref == -9999] <- NA

r_proj <- terra::project(x = r, y = ref, method = 'bilinear', threads = T, filename = paste0(outfile,'.tif'), overwrite = T)
terra::writeCDF(x = r_proj, filename = paste0(outfile,'.nc'), varname = var_name, longname = long_name, unit = var_units, compression = 9, overwrite = T)

# url <- 'https://isdasoil.s3.amazonaws.com/soil_data/aluminium_extractable/aluminium_extractable.tif'
# lyr_names <- c('aluminium_avg_00-20cm', 'aluminium_avg_20-50cm', 'aluminium_std_00-20cm', 'aluminium_std_20-50cm')
# var_name  <- 'aluminium_extractable'
# long_name <- 'Aluminium extractable'
# var_units <- 'ppm'
# outfile   <- paste0('//CATALOGUE/WFP_ClimateRiskPr1/agroclimExtremes/',gsub('.tif','',basename(url)))

# url <- 'https://isdasoil.s3.amazonaws.com/soil_data/bedrock_depth/bedrock_depth.tif'
# lyr_names <- c('bedrock_avg_00-200cm', 'bedrock_std_00-200cm')
# var_name  <- 'bedrock_depth'
# long_name <- 'Depth to bedrock'
# var_units <- 'cm'
# outfile   <- paste0('//CATALOGUE/WFP_ClimateRiskPr1/agroclimExtremes/',gsub('.tif','',basename(url)))

# url <- 'https://isdasoil.s3.amazonaws.com/soil_data/bulk_density/bulk_density.tif'
# lyr_names <- c('bulk_avg_00-20cm', 'bulk_avg_20-50cm', 'bulk_std_00-20cm', 'bulk_std_20-50cm')
# var_name  <- 'bulk_density'
# long_name <- 'Bulk density, <2mm fraction'
# var_units <- 'g/cc'
# outfile   <- paste0('//CATALOGUE/WFP_ClimateRiskPr1/agroclimExtremes/',gsub('.tif','',basename(url)))

# url <- 'https://isdasoil.s3.amazonaws.com/soil_data/calcium_extractable/calcium_extractable.tif'
# lyr_names <- c('calcium_avg_00-20cm', 'calcium_avg_20-50cm', 'calcium_std_00-20cm', 'calcium_std_20-50cm')
# var_name  <- 'calcium_extractable'
# long_name <- 'Calcium extractable'
# var_units <- 'ppm'
# outfile   <- paste0('//CATALOGUE/WFP_ClimateRiskPr1/agroclimExtremes/',gsub('.tif','',basename(url)))

# url <- 'https://isdasoil.s3.amazonaws.com/soil_data/carbon_organic/carbon_organic.tif'
# lyr_names <- c('carbon_avg_00-20cm', 'carbon_avg_20-50cm', 'carbon_std_00-20cm', 'carbon_std_20-50cm')
# var_name  <- 'carbon_organic'
# long_name <- 'Carbon organic'
# var_units <- 'g/kg'
# outfile   <- paste0('//CATALOGUE/WFP_ClimateRiskPr1/agroclimExtremes/',gsub('.tif','',basename(url)))

# url <- 'https://isdasoil.s3.amazonaws.com/soil_data/carbon_total/carbon_total.tif'
# lyr_names <- c('carbon_total_avg_00-20cm', 'carbon_total_avg_20-50cm', 'carbon_total_std_00-20cm', 'carbon_total_std_20-50cm')
# var_name  <- 'carbon_total'
# long_name <- 'Carbon total'
# var_units <- 'g/kg'
# outfile   <- paste0('//CATALOGUE/WFP_ClimateRiskPr1/agroclimExtremes/',gsub('.tif','',basename(url)))

# url <- 'https://isdasoil.s3.amazonaws.com/soil_data/cation_exchange_capacity/cation_exchange_capacity.tif'
# lyr_names <- c('cec_avg_00-20cm', 'cec_avg_20-50cm', 'cec_std_00-20cm', 'cec_std_20-50cm')
# var_name  <- 'cation_exchange_capacity'
# long_name <- 'Effective cation exchange capacity'
# var_units <- 'cmol(+)/kg'
# outfile   <- paste0('//CATALOGUE/WFP_ClimateRiskPr1/agroclimExtremes/',gsub('.tif','',basename(url)))

# url <- 'https://isdasoil.s3.amazonaws.com/soil_data/clay_content/clay_content.tif'
# lyr_names <- c('clay_avg_00-20cm', 'clay_avg_20-50cm', 'clay_std_00-20cm', 'clay_std_20-50cm')
# var_name  <- 'clay_content'
# long_name <- 'Clay content'
# var_units <- '%'
# outfile   <- paste0('//CATALOGUE/WFP_ClimateRiskPr1/agroclimExtremes/',gsub('.tif','',basename(url)))

# url <- 'https://isdasoil.s3.amazonaws.com/soil_data/fcc/fcc.tif'
# lyr_names <- c('fcc')
# var_name  <- 'fcc'
# long_name <- 'Fertility Capability Classification'
# var_units <- 'FCC categories'
# outfile   <- paste0('//CATALOGUE/WFP_ClimateRiskPr1/agroclimExtremes/',gsub('.tif','',basename(url)))

# url <- 'https://isdasoil.s3.amazonaws.com/soil_data/iron_extractable/iron_extractable.tif'
# lyr_names <- c('iron_avg_00-20cm', 'iron_avg_20-50cm', 'iron_std_00-20cm', 'iron_std_20-50cm')
# var_name  <- 'iron_extractable'
# long_name <- 'Iron extractable'
# var_units <- 'ppm'
# outfile   <- paste0('//CATALOGUE/WFP_ClimateRiskPr1/agroclimExtremes/',gsub('.tif','',basename(url)))

url <- 'https://isdasoil.s3.amazonaws.com/soil_data/magnesium_extractable/magnesium_extractable.tif'
lyr_names <- c('magnesium_avg_00-20cm', 'magnesium_avg_20-50cm', 'magnesium_std_00-20cm', 'magnesium_std_20-50cm')
var_name  <- 'magnesium_extractable'
long_name <- 'Magnesium extractable'
var_units <- 'ppm'
outfile   <- paste0('//CATALOGUE/WFP_ClimateRiskPr1/agroclimExtremes/iSDA/',gsub('.tif','',basename(url)))
