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
#/home/ec2-user/anaconda3/bin/python downloadChirpsMonthly.py
/home/ec2-user/anaconda3/bin/python getMonthS3toNC.py --execution_type manual --year 2023 --month "09"
/home/ec2-user/anaconda3/bin/python appendToZarr.py