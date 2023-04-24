#!/usr/bin/python
import os
import boto
import json
from datetime import *
import time

AWS_ACCESS_KEY_ID = 'AKIAJDKZB5KNVX6YMLJQ'
AWS_SECRET_ACCESS_KEY = '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'

con = boto.connect_s3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
bucket = con.get_bucket('nfdelivery-carrier')

while True:
    found=False
    try:
        now=datetime.now()
        drivers=json.loads(open("/tmp/nfd-drivers.json").read())
        active={}
        for login,data in drivers.items():
            d=datetime.strptime(data["receive_time"],"%Y-%m-%d %H:%M:%S")
            if (now-d).seconds<=300:
                active[login]=data
        print(active)
        k=bucket.new_key("active-drivers")
        k.set_contents_from_string(json.dumps(active))
    except:
        import traceback
        traceback.print_exc()
    time.sleep(5)
