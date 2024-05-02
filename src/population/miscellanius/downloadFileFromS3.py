import os
import argparse
import logging
from yaml import safe_load


def downloadDataFromS3FilteredByYear(s3Path: str
                                     , downloadPath: str
                                     ,file:str
                                     , year:str 
                                     , month : str
                                    ):
    
    s3Command = f'aws s3 cp {s3Path} {downloadPath} --recursive --exclude "*" --include "{file}{year}{month}*"'
    print(s3Command)
    return os.system(s3Command)

def main():
    logging.info("Starting download routine")
    parser = argparse.ArgumentParser()
    parser.add_argument('--confType', type=str)
    parser.add_argument('--year', type=str)
    parser.add_argument('--month', type=str)
    # Read configuration from YAML (not shown here for brevity)
    ymlPath = os.environ["DATALAKE_CONF_PATH"]
    conf_args = safe_load(open(ymlPath, 'r'))  # Use safe_load for security
    args = parser.parse_args()
    confFile = conf_args[args.confType]
    s3Path = confFile["s3Landing"]
    downloadPath = confFile["pathforLanding"]
    year  = args.year
    month = args.month
    file = confFile["fileName"]

    downloadDataFromS3FilteredByYear(
        s3Path = s3Path,
        downloadPath = downloadPath,
        file = file,
        year = year,
        month = month

    )

if __name__ == '__main__':
    main()