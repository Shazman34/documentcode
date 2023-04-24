from netforce.model import Model,fields,get_model
import requests
import json
from decimal import *
from pprint import pprint

class API(Model):
    _name="maps.api"
    _store=False

    def get_distance(self,from_coords,to_coords,context={}):
        api_key="AIzaSyAXEHOYaPzi7gTusKIsTNSV-lUtxWSPm-g"
        url="https://maps.googleapis.com/maps/api/distancematrix/json?origins=%s&destinations=%s&key=%s"%(from_coords,to_coords,api_key)
        r=requests.get(url,timeout=5)
        res=json.loads(r.text)
        dist=Decimal(res["rows"][0]["elements"][0]["distance"]["value"])/1000
        duration=Decimal(res["rows"][0]["elements"][0]["duration"]["value"])/60
        return {"distance":dist,"duration":duration}

API.register()
