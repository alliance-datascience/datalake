options(warn = -1, scipen = 999)
suppressMessages(if(!require(pacman)){install.packages('pacman');library(pacman)} else {library(pacman)})
suppressMessages(pacman::p_load(terra, ncdf4, geodata))

vrs <- c('bdod','cfvo','clay','nitrogen','ocd','ocs','phh2o','sand','silt','soc')
dpt <- c(5,15,30,60,100,200)
sts <- c('mean','uncertainty','Q0.05','Q0.5','Q0.95')

# Setup table
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
                             long_name  = 'World Reference Base Soil Groups',
                             var_units  = NA,
                             soil_group = c('Acrisols', 'Albeluvisols', 'Alisols', 'Andosols', 'Arenosols', 'Calcisols', 'Cambisols', 'Chernozems', 'Cryosols', 'Durisols', 'Ferralsols', 'Fluvisols', 'Gleysols', 'Gypsisols', 'Histosols', 'Kastanozems', 'Leptosols', 'Lixisols', 'Luvisols', 'Nitisols', 'Phaeozems', 'Planosols', 'Plinthosols', 'Podzols', 'Regosols', 'Solonchaks', 'Solonetz', 'Stagnosols', 'Umbrisols', 'Vertisols')))

var_name  = stp$var_name[1]
var_depth = stp$var_depth[1]
var_stats = stp$var_stats[1]

# Virtual connection to SoilGrids 250m version 2.0
if(var_name == 'wrb'){
  r <- geodata::soil_world_vsi(var = var_name, name = soil_group)
} else {
  r <- geodata::soil_world_vsi(var = var_name, depth = var_depth, stat = var_stats)
}

label_stats <- dplyr::case_when(var_stats == 'mean' ~ 'avg',
                                var_stats == 'uncertainty' ~ 'std',
                                var_stats == 'Q0.05' ~ 'q05',
                                var_stats == 'Q0.5' ~ 'q50',
                                var_stats == 'Q0.95' ~ 'q95')
label_depth <- dplyr::case_when(var_depth == '5' ~ '00-05cm',
                                var_depth == '15' ~ '05-15cm',
                                var_depth == '30' ~ '15-30cm',
                                var_depth == '60' ~ '30-60cm',
                                var_depth == '100' ~ '60-100cm',
                                var_depth == '200' ~ '100-200cm')

names(r) <- paste0(var_name,'_',label_stats,'_',label_depth)

# Reference raster (CHIRPS)
chirps_ref <- 'https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_daily/tifs/p05/2023/chirps-v2.0.2023.01.01.tif.gz'
ref <- terra::rast(paste0('/vsigzip//vsicurl/',chirps_ref)); rm(chirps_ref)
ref[ref == -9999] <- NA

outdir <- '//CATALOGUE/WFP_ClimateRiskPr1/agroclimExtremes/SoilGrids'

r_proj <- terra::project(x = r, y = ref, method = 'bilinear', threads = T, filename = paste0(outdir,'/',names(r),'.tif'), overwrite = T)
terra::writeCDF(x = r_proj, filename = paste0(outfile,'.nc'), varname = var_name, longname = long_name, unit = var_units, compression = 9, overwrite = T)
gc(verbose=F, full=T, reset=T)
