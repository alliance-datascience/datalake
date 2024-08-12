#!/usr/bin/env python
# coding: utf-8

import sys
import luigi
import os
srcPath = os.environ["SRC_CODE"]
confFileY = os.environ["DATALAKE_CONF_PATH"]
sys.path.append(srcPath)
from population.miscellanius import S3utilities
from population.sources.agera import downloadData
from population.sources.agera.solarRadiationFlux import appendIntoZarr
import glob
from yaml import safe_load

confType = "agera5ArgumentsSolarFlux"
year = 2023
month = "10"
variable = "solar_radiation_flux"
conf_args = safe_load(open(confFileY, 'r'))
conf_args = conf_args[confType]


class getDatafromAgera(luigi.Task):
    confType = luigi.Parameter()
    year = luigi.Parameter()
    month = luigi.Parameter()
    variable = luigi.Parameter()

    def run(self):
        downloadData.downloadAgera(self.confType,
                                   self.year,
                                   self.month,
                                   self.variable)
        with self.output().open('w') as f:
            print("OK", file=f)
    def output(self):
        return luigi.LocalTarget('/tmp/getDatafromAgera.txt')


class downloadDataFromS3(luigi.Task):
    confType = luigi.Parameter()
    year = luigi.Parameter()
    month = luigi.Parameter()
    variable = luigi.Parameter()

    def requires(self):
        return getDatafromAgera(self.confType,
                                self.year,
                                self.month,
                                self.variable)


    def run(self):
        S3utilities.S3Operations(
            self.confType,
            self.year,
            self.month
        )
        with self.output().open('w') as f:
            print("OK", file=f)

    def output(self):
        return luigi.LocalTarget('/tmp/downloadDataFromS3.txt')




class changeResolution(luigi.Task):
    confType = luigi.Parameter()
    year = luigi.Parameter()
    month = luigi.Parameter()
    variable = luigi.Parameter()

    def requires(self):
        return downloadDataFromS3(self.confType,
                                  self.year,
                                  self.month,
                                  self.variable)
    def run(self):
        pathZip = conf_args["pathforLanding"]+"*.zip"
        for f in glob.glob(pathZip) :
            os.remove(f)
        rPath = srcPath + "/population/miscellanius/resampledR.r"
        rCommand= f"Rscript  {rPath} {confType} "
        commandResult = os.system(rCommand)
        if commandResult != 0:
            raise Exception("Rscript with error")

        with self.output().open('w') as f:
            print("OK", file=f)

    def output(self):
        return luigi.LocalTarget('/tmp/changeResolution.txt')

class deleteUnusedFiles(luigi.Task):


    confType = luigi.Parameter()
    year = luigi.Parameter()
    month = luigi.Parameter()
    variable = luigi.Parameter()

    def requires(self):
        return changeResolution(self.confType,
                                  self.year,
                                  self.month,
                                  self.variable)
    def run(self):
        filesForDelete = conf_args["pathforReggrid"]+"*.json"
        for filename in glob.glob(filesForDelete):
            os.remove(filename)
        filesForDelete = conf_args["pathforReggrid"]+"*.xml"
        for filename in glob.glob(filesForDelete):
            os.remove(filename)
        with self.output().open('w') as f:
            print("OK", file=f)

    def output(self):
        return luigi.LocalTarget('/tmp/deleteUnusedFiles.txt')


class appendZarrFiles(luigi.Task):

    confType = luigi.Parameter()
    year = luigi.Parameter()
    month = luigi.Parameter()
    variable = luigi.Parameter()

    def requires(self):
        return deleteUnusedFiles(self.confType,
                                 self.year,
                                 self.month,
                                 self.variable)

    def run(self):
        appendIntoZarr.appendIntoZarr()
        with self.output().open('w') as f:
            print("OK", file=f)

    def output(self):
        return luigi.LocalTarget('/tmp/appendZarrFiles.txt')
    
class deleteUsedFiles(luigi.Task):

    confType = luigi.Parameter()
    year = luigi.Parameter()
    month = luigi.Parameter()
    variable = luigi.Parameter()

    def requires(self):
        return appendZarrFiles(self.confType,
                                  self.year,
                                  self.month,
                                  self.variable)
    def run(self):
        filesForDelete = conf_args["pathforLanding"]+"*"
        for filename in glob.glob(filesForDelete):
            os.remove(filename)
        filesForDelete = conf_args["pathforReggrid"]+"*"
        for filename in glob.glob(filesForDelete):
            os.remove(filename)
        filesForDelete = conf_args["pathforStandardized"]+"*"
        for filename in glob.glob(filesForDelete):
            os.remove(filename)
        with self.output().open('w') as f:
            print("OK", file=f)

    def output(self):
        return luigi.LocalTarget('/tmp/deleteUsedFiles.txt')

if __name__ == "__main__":

    luigi.build([deleteUsedFiles(confType=confType,
                                 year=year,
                                 month=month, variable=variable)],
                local_scheduler=True)

