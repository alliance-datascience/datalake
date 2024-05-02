#!/usr/bin/env python
# coding: utf-8



import sys
import luigi
import os
srcPath = os.environ["SRC_CODE"]
sys.path.append(srcPath)
from population.miscellanius import S3utilities
from population.sources.agera import downloadData

confType = "agera5ArgumentsSolarFlux"
year = 2024
month = "01"
variable = "solar_radiation_flux"

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
        print("Hola mundo")
        with self.output().open('w') as f:
            print("OK", file=f)

    def output(self):
        return luigi.LocalTarget('/tmp/changeResolution.txt')



if __name__ == "__main__" :
    luigi.build([changeResolution(confType=confType,
                                  year=year,
                                  month=month,
                                  variable=variable)],
                local_scheduler=True)

