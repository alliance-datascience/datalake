#!/usr/bin/env python
# coding: utf-8

# In[5]:


import os
import requests
import boto3
from datetime import datetime, timedelta
import pandas as pd


# In[19]:


twoMonthsDate = (datetime.now()-timedelta(days=60))
year = [int(twoMonthsDate.strftime('%Y'))]
month = [int(twoMonthsDate.strftime('%m'))]


# In[20]:


# input_path = "/home/ec2-user/data"
bucket = "climate-action-datalake"

s3_client = boto3.client('s3')


# In[21]:


variable_name = ["precipitation"]
url = "https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_daily/tifs/p05"
days=range(1,32)
arrUrl = []
fileFormat = "tif.gz"


# In[24]:


def generate_chirts_URL(years
                         , months
                         ,days
                         ,variables,url
                         ,fileFormat):
    _arrUrl = []
    for _variable in variables:
        for _year in years:
            for _month in months:
                for _day in days:
                    _arrUrl.append(url+"/"+str(_year)+"/"
                                   +f"chirps-v2.0.{_year}.{_month:02d}.{_day:02d}.{fileFormat}")
    return _arrUrl

def download_data(arrUrl,s3_directory,zone,source,variable):
    for _url in arrUrl:
        response = requests.get(_url)
        if response.status_code == 200 :
            file_path = os.path.basename(_url)
#             with open(file_path, 'wb') as file:
#                 for chunk in response.iter_content(chunk_size=1024):
#                     if chunk:
#                         file.write(chunk)
            s3_client.put_object(Bucket=bucket
                                 ,Key=f"zone={zone}/source={source}/variable={variable}/"+file_path
                                 ,Body=response.content
                                )
            print(file_path)

        else:
            print("NOk")


# In[25]:


arrUrl = generate_chirts_URL(year,month,days,variable_name,url,fileFormat)


# In[26]:


download_data(arrUrl,bucket,"landing","CHIRPS","precipitation")

