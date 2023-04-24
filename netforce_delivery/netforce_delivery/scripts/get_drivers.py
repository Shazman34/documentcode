#!/usr/bin/env python
import boto.sqs
from datetime import *
import time
from pprint import pprint
import json
import requests
from boto.sqs.message import RawMessage
import psycopg2

boto_con=boto.sqs.connect_to_region(
    "ap-southeast-1",
    aws_access_key_id="AKIAJDKZB5KNVX6YMLJQ",
    aws_secret_access_key="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",
)

q=boto_con.get_queue("nfdelivery-carrier")
q.set_message_class(RawMessage)

db=psycopg2.connect(database="nfdelivery", user="datrus", password="sqlblabla")

def get_cell_coords(cid,lac,mnc,mcc):
    #print("#"*80)
    #print("get_cell_coords",cid,lac,mnc,mcc)
    cr=db.cursor()
    cr.execute("select coords from nd_cell where mcc=%s and mnc=%s and lac=%s and cid=%s",(str(mcc),str(mnc),str(lac),str(cid)))
    res=cr.fetchone()
    if res:
        #print("got cell coords from db: %s"%res[0])
        return res[0]
    key="AIzaSyAnOTbaAFeCz6YM_eIkv_oaHpc-eSsV8Ho"
    url="https://www.googleapis.com/geolocation/v1/geolocate?key=%s"%key
    data={
        "cellTowers": [
            {
                "cellId": cid,
                "locationAreaCode": lac,
                "mobileCountryCode": mcc,
                "mobileNetworkCode": mnc,
            },
        ],
    }
    #print("data",data)
    try:
        r = requests.post(url, json=data, timeout=15)
        res=r.json()
        #print("res",res)
    except Exception as e:
        print("geolocate request failed: %s",e)
        return None
    try:
        acc=res["accuracy"]
        lat=res["location"]["lat"]
        lng=res["location"]["lng"]
        coords="%s,%s"%(lat,lng)
        #print("got cell coords: %s"%coords)
    except:
        acc=None
        coords=None
        #print("cell coords not found")
    cr.execute("insert into nd_cell (cid,lac,mnc,mcc,coords,accuracy) values (%s,%s,%s,%s,%s,%s)",(str(cid),str(lac),str(mnc),str(mcc),coords,acc))
    db.commit()
    return coords

drivers={}

while True:
    try:
        rs=q.get_messages(10)
    except:
        import traceback
        traceback.print_exc()
        time.sleep(5)
        continue
    print("%d messages"%len(rs))
    found=False
    for m in rs:
        try:
            body=m.get_body()
            data=json.loads(body)
            upload_time=data["Records"][0]["eventTime"]
            path=data["Records"][0]["s3"]["object"]["key"]
            print("new file: %s"%path)
            if path.endswith("/latest-status"):
                login,_,filename=path.partition("/")
                url="https://s3-ap-southeast-1.amazonaws.com/nfdelivery-carrier/%s/latest-status"%login
                r=requests.get(url)
                #print("status",r.content)
                data=r.json()
                data["receive_time"]=time.strftime("%Y-%m-%d %H:%M:%S")
                if not data.get("loc"):
                    cells=data.get("cells")
                    if cells:
                        cell=cells[0]
                        mcc=cell.get("mcc")
                        if mcc is None:
                            mcc=data.get("mcc")
                        mnc=cell.get("mnc")
                        if mnc is None:
                            #mnc=data.get("mnc")
                            mnc=data.get("mnc") or 0 # XXX: remove "or o"
                        cid=cell.get("cid") or cell.get("ci") or cell.get("bid")
                        lac=cell.get("lac") or cell.get("tac")
                        if mcc is not None and mnc is not None and cid is not None and lac is not None:
                            data["cell_loc"]=get_cell_coords(cid,lac,mnc,mcc)
                        else:
                            print("!"*80)
                            print("Missing cell data")
                    else:
                        print("!"*80)
                        print("No cells")
                drivers[login]=data
                #print("=> %s %s"%(login,data))
                open("/tmp/nfd-drivers.json","w").write(json.dumps(drivers))
        except:
            import traceback
            traceback.print_exc()
        q.delete_message(m)
        found=True
    if not found:
        print("no new messages, sleeping 1s")
        time.sleep(1)
