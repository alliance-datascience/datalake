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

outdir <- '//CATALOGUE/WFP_ClimateRiskPr1/agroclimExtremes/iSDA'

## Reading setup table ----
stp <- readxl::read_excel(path = paste0(outdir,'/soils_metadata.xlsx'), sheet = 'stp') |> base::as.data.frame()

## Resampling function using GDAL ----
iSDA_GDAL_processing <- function(var_url, var_name, var_band, var_depth, var_stats, var_units, long_name, outdir){
  
  # URL
  u <- var_url
  # Variable band
  
  # Check if the file corresponds to table or raster
  if(strsplit(basename(u), split = '\\.')[[1]][2] == 'csv'){
    download.file(url = u, destfile = paste0(outdir,'/',basename(u)), mode = 'wb')
  } else {
    u <- paste0('/vsicurl/',u)
    
    if(any(is.na(c(var_depth,var_stats)))){
      outfile <- gsub('.tif','',basename(u))
    } else {
      outfile <- paste0(gsub('.tif','',basename(u)),'_',var_depth,'_',var_stats)
    }
    
    if(!file.exists(paste0(outdir,'/',outfile,'.nc'))){
      # Temporal vrt rasters
      intrmd_vrt <- paste0(tempfile(),'.vrt') # Intermediate raster
      output_vrt <- paste0(tempfile(),'.vrt') # Final raster
      
      ## GDAL operations
      # gdalbuildvrt -b 1 -resolution highest -r nearest "output.vrt" "input.tif"
      # gdalwarp -t_srs EPSG:4326 output.vrt output_warped.vrt
      
      # Resample to 5x5km
      gdalUtilities::gdalbuildvrt(gdalfile = u, output.vrt = intrmd_vrt, b = var_band, resolution = 'user', tr = c(5500, 5500), r = ifelse(var_name %in% c('fcc','texture_class'),'nearest','bilinear'))
      # Original CRS to EPSG:4326
      gdalUtilities::gdalwarp(srcfile = intrmd_vrt, dstfile = output_vrt, t_srs = 'EPSG:4326')
      
      # Load GDAL vrt result
      r <- terra::rast(output_vrt)
      # Write GDA: vrt result to tif
      terra::writeRaster(x = r, filename = paste0(outdir,'/',outfile,'_intrmd.tif'), overwrite = T)
      r <- terra::rast(paste0(outdir,'/',outfile,'_intrmd.tif'))
      names(r) <- outfile
      
      # Reference raster (CHIRPS)
      chirps_ref <- 'https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_daily/tifs/p05/2023/chirps-v2.0.2023.01.01.tif.gz'
      ref <- terra::rast(paste0('/vsigzip//vsicurl/',chirps_ref)); rm(chirps_ref)
      ref[ref == -9999] <- NA
      
      # Save resampled raster into tif and nc formats
      r_rsmp <- terra::resample(x = r, y = ref, method = ifelse(var_name %in% c('fcc','texture_class'),'near','bilinear'), threads = T, filename = paste0(outdir,'/',outfile,'.tif'), overwrite = T)
      terra::writeCDF(x = r_rsmp, filename = paste0(outdir,'/',outfile,'.nc'), varname = var_name, longname = long_name, unit = var_units, compression = 9)
    } else {
      cat('File already processed\n')
    }
    
  }
  
  return(cat('Done ... next\n'))
  
}

## Loop over setup table ----
for(i in 1:nrow(stp)){
  iSDA_GDAL_processing(var_url = stp$url[i],
                       var_name = stp$var_name[i],
                       var_band = stp$var_band[i],
                       var_depth = stp$var_depth[i],
                       var_stats = stp$var_stats[i],
                       var_units = stp$var_units[i],
                       long_name = stp$long_name[i],
                       outdir = outdir)
  cat(paste0('Progress ',round(i/nrow(stp) * 100, 2),'%, Row: ',i,'\n'))
}
