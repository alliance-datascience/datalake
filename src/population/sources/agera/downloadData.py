import os
from zipfile import ZipFile
import glob
import boto3

import logging
from yaml import safe_load  # Use safe_load for security reasons
from cdsapi import Client  # Import Client directly

class downloadAgera:
    def download_agera5_data(self,
                             variable_name,
                             year,
                             month,
                             day,
                             bucket,
                             download_path,
                             zip_name,
                             datalake_zone, source, s3_variable_name, url,
                             key):
        """Downloads AgERA5 data and uploads it to S3.

        Args:
            variable_name (str): Name of the variable to download.
            year (int): Year to download data for.
            month (int): Month to download data for.
            day (list): List of days to download data for. Defaults to all days.
            bucket (str): S3 bucket name to upload data to.
            download_path (str): Local path to download data to.
            zip_name (str): Name of the zip file to download.
            datalake_zone (str): Zone in the data lake to upload data to.
            source (str): Source of the data (e.g., "agera5").
            s3_variable_name (str): Name of the variable used in S3 path.
            url (str): URL of the Copernicus Climate Data Store.
            key (str): API key for accessing the Copernicus Climate Data Store.
        """

        cds = Client(url=url, key=key)
        sis_k = "sis-agrometeorological-indicators"

        for _day in day:
            json_copernicus = {
                'format': 'zip',
                'version': '1_1',
                'variable': variable_name,
                'year': [str(year)],
                'month': [f"{int(month):02d}"],
                'day': [f"{_day:02d}"],
                'time': '12_00'
            }

            try:
                cds.retrieve(sis_k, json_copernicus, os.path.join(download_path, zip_name))

                with ZipFile(os.path.join(download_path, zip_name), 'r') as z:
                    z.extractall(path=download_path)

                files_upload = glob.glob(os.path.join(download_path, "*.nc"))
                s3_client = boto3.client('s3')

                for _file in files_upload:
                    s3_path = f"zone={datalake_zone}/source={source}/variable={s3_variable_name}/"
                    print(_file, s3_path, os.path.join(s3_path, _file.split("/")[-1]))
                    response = s3_client.upload_file(_file, bucket, os.path.join(s3_path, _file.split("/")[-1]))
                    os.remove(_file)

            except Exception as e:
                logging.error("Error downloading data for:", variable_name, year, month, exc_info=e)


    def __init__(self,
                 confType,
                 year,
                 month,
                 variable
                ):
        """Parses arguments and calls download function."""
        key="187933:64547c55-b131-4cec-a39e-f455bf2b12b3"
        url = "https://cds.climate.copernicus.eu/api/v2"
        user = "129570"
        bucket = "climate-action-datalake"
        localDownloadPath = "data/"
        zip_name = "sample.zip"
        datalakeZone = "landing"
        source = "agera5"
        self.confType = confType
        self.year = year
        self.month = month
        self.variable = variable

        logging.info("Starting download routine")

        # Read configuration from YAML (not shown here for brevity)
        ymlPath = os.environ["DATALAKE_CONF_PATH"]
        conf_args = safe_load(open(ymlPath, 'r'))  # Use safe_load for security
        agera5_args = conf_args[self.confType]

        self.download_agera5_data(
            variable_name=self.variable,
            year=self.year,
            month=self.month,
            day=range(1, 32),  # Default to all days
            bucket=bucket,
            download_path=agera5_args['pathforLanding'],
            zip_name=zip_name,
            datalake_zone=datalakeZone,
            source=source,
            s3_variable_name=agera5_args['s3VariableName'],
            url=url,
            key=key
        )


