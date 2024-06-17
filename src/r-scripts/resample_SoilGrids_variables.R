# ------------------------------------------ #
# Resampling SoilGrids dataset
# By: Harold Achicanoy
# Alliance Bioversity CIAT
# June 2024
# ------------------------------------------ #

## R options and packages loading ----
options(warn = -1, scipen = 999)
suppressMessages(if(!require(pacman)){install.packages('pacman');library(pacman)} else {library(pacman)})
suppressMessages(pacman::p_load(terra, ncdf4, geodata, gdalUtilities))

## Creating setup table ----
vrs <- c('bdod','cfvo','clay','nitrogen','ocd','ocs','phh2o','sand','silt','soc')
dpt <- c(5,15,30,60,100,200)
sts <- c('mean','uncertainty','Q0.05','Q0.5','Q0.95')

stp <- base::expand.grid(vrs, dpt, sts); rm(vrs, dpt, sts)
names(stp) <- c('var_name','var_depth','var_stats')
stp <- stp |> dplyr::mutate(long_name = dplyr::case_when(var_name == 'bdod' ~ 'Bulk density of the fine earth fraction',
                                                         var_name == 'cec' ~ 'Cation Exchange Capacity of the soil',
                                                         var_name == 'cfvo' ~ 'Vol. fraction of coarse fragments (> 2 mm)',
                                                         var_name == 'nitrogen' ~ 'Total nitrogen (N)',
                                                         var_name == 'phh2o' ~ 'pH (H2O)',
                                                         var_name == 'sand' ~ 'Sand (> 0.05 mm) in fine earth',
                                                         var_name == 'silt' ~ 'Silt (0.002-0.05 mm) in fine earth',
                                                         var_name == 'clay' ~ 'Clay (< 0.002 mm) in fine earth',
                                                         var_name == 'soc' ~ 'Soil organic carbon in fine earth',
                                                         var_name == 'ocd' ~ 'Organic carbon density',
                                                         var_name == 'ocs' ~ 'Organic carbon stocks'),
                            var_units = dplyr::case_when(var_name == 'bdod' ~ 'cg cm-3',
                                                         var_name == 'cec' ~ 'mmol(+) kg-1',
                                                         var_name == 'cfvo' ~ '%',
                                                         var_name == 'nitrogen' ~ 'cg kg-1',
                                                         var_name == 'phh2o' ~ 'pH units',
                                                         var_name == 'sand' ~ '%',
                                                         var_name == 'silt' ~ '%',
                                                         var_name == 'clay' ~ '%',
                                                         var_name == 'soc' ~ 'dg kg-1',
                                                         var_name == 'ocd' ~ 'hg m-3',
                                                         var_name == 'ocs' ~ 'hg m-2')) |>
  base::as.data.frame()
stp$soil_group <- NA
stp <- rbind(stp, data.frame(var_name = 'wrb', var_depth = NA, var_stats = NA,
                             long_name  = 'WRBSG',
                             var_units  = NA,
                             soil_group = c('Acrisols', 'Albeluvisols', 'Alisols', 'Andosols', 'Arenosols', 'Calcisols', 'Cambisols', 'Chernozems', 'Cryosols', 'Durisols', 'Ferralsols', 'Fluvisols', 'Gleysols', 'Gypsisols', 'Histosols', 'Kastanozems', 'Leptosols', 'Lixisols', 'Luvisols', 'Nitisols', 'Phaeozems', 'Planosols', 'Plinthosols', 'Podzols', 'Regosols', 'Solonchaks', 'Solonetz', 'Stagnosols', 'Umbrisols', 'Vertisols')))
stp <- stp |>
  dplyr::mutate_all(as.character) |>
  base::as.data.frame()
stp$var_depth <- as.numeric(stp$var_depth)
stp <- stp[-which(stp$var_name == 'ocs' & stp$var_depth != 30),]
stp$long_name[stp$var_name == 'wrb'] <- paste0(stp$long_name[stp$var_name == 'wrb'],'-',stp$soil_group[stp$var_name == 'wrb'])
stp$var_units[stp$var_name == 'wrb'] <- 'Probability'
rownames(stp) <- 1:nrow(stp)

outdir <- '//CATALOGUE/WFP_ClimateRiskPr1/agroclimExtremes/SoilGrids'

## Resampling function using GDAL ----
GDAL_processing <- function(var_name, var_depth, var_stats, var_units, long_name, soil_group, outdir){
  
  # Virtual connection to SoilGrids 250m version 2.0
  if(var_name == 'wrb'){
    u <- geodata:::.soil_grids_url(var = var_name, name = soil_group, vsi = T)
  } else {
    u <- geodata:::.soil_grids_url(var = var_name, depth = var_depth, stat = var_stats, vsi = T)
  }
  
  if(!file.exists(paste0(outdir,'/',gsub('.vrt','.nc',basename(u))))){
    
    # Temporal vrt rasters
    intrmd_vrt <- paste0(tempfile(),'.vrt') # Intermediate raster
    output_vrt <- paste0(tempfile(),'.vrt') # Final raster
    
    ## GDAL operations
    # gdalbuildvrt -b 1 -resolution highest -r nearest "output.vrt" "input.tif"
    # gdalwarp -t_srs EPSG:4326 output.vrt output_warped.vrt
    
    # Resample to 5x5km
    if(var_name == 'wrb'){
      gdalUtilities::gdalbuildvrt(gdalfile = u, output.vrt = intrmd_vrt, b = 1, resolution = 'user', tr = c(0.05, 0.05), r = 'bilinear')
    } else {
      gdalUtilities::gdalbuildvrt(gdalfile = u, output.vrt = intrmd_vrt, b = 1, resolution = 'user', tr = c(5500, 5500), r = 'bilinear')
    }
    # Original CRS to EPSG:4326
    gdalUtilities::gdalwarp(srcfile = intrmd_vrt, dstfile = output_vrt, t_srs = 'EPSG:4326')
    
    # Load GDAL vrt result
    r <- terra::rast(output_vrt)
    # Write GDA: vrt result to tif
    terra::writeRaster(x = r, filename = paste0(outdir,'/',gsub('.vrt','',basename(u)),'_intrmd.tif'), overwrite = T)
    r <- terra::rast(paste0(outdir,'/',gsub('.vrt','',basename(u)),'_intrmd.tif'))
    
    # Reference raster (CHIRPS)
    chirps_ref <- 'https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_daily/tifs/p05/2023/chirps-v2.0.2023.01.01.tif.gz'
    ref <- terra::rast(paste0('/vsigzip//vsicurl/',chirps_ref)); rm(chirps_ref)
    ref[ref == -9999] <- NA
    
    # Save resampled raster into tif and nc formats
    r_rsmp <- terra::resample(x = r, y = ref, method = 'bilinear', threads = T, filename = paste0(outdir,'/',gsub('.vrt','.tif',basename(u))), overwrite = T)
    terra::writeCDF(x = r_rsmp, filename = paste0(outdir,'/',gsub('.vrt','.nc',basename(u))), varname = var_name, longname = long_name, unit = var_units, compression = 9)
    
  } else {
    cat('File already processed\n')
  }
  
  return(cat('Done ... next\n'))
  
}

## Loop over setup table ----
for(i in 1:nrow(stp)){
  GDAL_processing(var_name   = stp$var_name[i],
                  var_depth  = stp$var_depth[i],
                  var_stats  = stp$var_stats[i],
                  var_units  = stp$var_units[i],
                  long_name  = stp$long_name[i],
                  soil_group = stp$soil_group[i],
                  outdir     = outdir)
  cat(paste0('Progress ',round(i/nrow(stp) * 100, 2),'%, Row: ',i,'\n'))
}
