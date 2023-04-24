#!/usr/bin/env python
import requests
from pprint import pprint
import json

key="AIzaSyAnOTbaAFeCz6YM_eIkv_oaHpc-eSsV8Ho"
url="https://www.googleapis.com/geolocation/v1/geolocate?key=%s"%key
data={
    "cellTowers": [
#        {
#            "cellId": 42040828,
#            "locationAreaCode": 7025,
#            "mobileCountryCode": 520,
#            "mobileNetworkCode": 3,
#        },
#        {
#            "cellId": 798844,
#            "locationAreaCode": 8,
#            "mobileCountryCode": 520,
#            "mobileNetworkCode": 0,
#        },
#        {
#            "cellId": 10005526,
#            "locationAreaCode": 1015,
#        },
        {
            "cellId": 64585474,
            "locationAreaCode": 3142,
            "mobileCountryCode": 520,
            "mobileNetworkCode": 18,
        },
    ],
}
r = requests.post(url, json=data)
res=r.json()
pprint(res)
