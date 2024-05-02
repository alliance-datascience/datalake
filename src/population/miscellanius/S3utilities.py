import os
import logging
from yaml import safe_load

class S3Operations:
    def downloadDataFromS3Filtered(self,
                                   s3Path: str
                                         , downloadPath: str
                                         ,file:str
                                         , year:str 
                                         , month : str
                                        ):

        s3Command = f'aws s3 cp {s3Path} {downloadPath} --recursive --exclude "*" --include "{file}{year}{month}*"'
        print(s3Command)
        return os.system(s3Command)

    def __init__(self,
                 confType,
                 year,
                 month):
        logging.info("Starting download routine")
        self.confType = confType
        self.year = year
        self.month = month
        # Read configuration from YAML (not shown here for brevity)
        ymlPath = os.environ["DATALAKE_CONF_PATH"]
        conf_args = safe_load(open(ymlPath, 'r'))  # Use safe_load for security
        confFile = conf_args[self.confType]
        s3Path = confFile["s3Landing"]
        print(s3Path)
        downloadPath = confFile["pathforLanding"]
        year = self.year
        month = self.month
        file = confFile["fileName"]

        self.downloadDataFromS3Filtered(
            s3Path = s3Path,
            downloadPath = downloadPath,
            file = file,
            year = year,
            month = month

        )

