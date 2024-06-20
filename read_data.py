import csv
import os
from io import StringIO
from google.cloud import storage 
from google.cloud.vision_v1 import types
from google.cloud import vision
import pandas as pd
from flask import Flask,redirect,url_for,render_template,request
os.environ['GOOGLE_APPLICATION_CREDENTIALS']='perfect-spanner-425011-k8-d984436dc102.json'

from flask import Flask,redirect,url_for,render_template,request

storage_client = storage.Client()
bucket = storage_client.get_bucket('warehouse1_data')
blob = bucket.blob('Final_Updated_data.csv')
blob = blob.download_as_string()

blob = blob.decode('utf-8')

blob = StringIO(blob)
df = pd.read_csv(blob)
# print(df)
