#!/bin/bash/
cd nc/  
rm -rf *.nc 
cd ..
cd tgz/
rm -rf *.tif 
cd ..
cd tgz/ 
rm -rf *.gz 
cd ..

set -e
/home/ubuntu/anaconda/bin/python downloadChirpsMonthly.py
/home/ubuntu/anaconda/bin/python getMonthS3toNC.py --execution_type auto
/home/ubuntu/anaconda/bin/python appendToZarr.py
