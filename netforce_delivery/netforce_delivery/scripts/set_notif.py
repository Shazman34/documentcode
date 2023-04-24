#!/usr/bin/python
import os
import boto
import json
from datetime import *
import time
import sys

carrier_id=sys.argv[1]
notif_id=int(sys.argv[2])
notif_title=sys.argv[3]
notif_text=sys.argv[4]

AWS_ACCESS_KEY_ID = 'AKIAJDKZB5KNVX6YMLJQ'
AWS_SECRET_ACCESS_KEY = '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'

con = boto.connect_s3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
bucket = con.get_bucket('nfdelivery-carrier')

data={
    "id": notif_id,
    "title": notif_title,
    "text": notif_text,
}
k=bucket.new_key("%s/notif"%carrier_id)
k.set_contents_from_string(json.dumps(data))
