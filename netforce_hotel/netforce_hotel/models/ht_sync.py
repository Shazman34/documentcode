from netforce.model import Model,fields,get_model
from netforce import tasks
import time
import requests

CLIENT_ID="live1_9518_XEOJRdqaLz36EDdEkl0yVEAI"
CLIENT_SECRET="8eDJJvNQei6ZIvQnHOcwaOcNFfA0djW0"
REDIRECT_URI="https://backend.netforce.com/cloudbeds_authorize?db=nfo_grace"

class Sync(Model):
    _name="ht.sync"
    _fields={
        "oauth_code": fields.Char("Oauth Code"),
        "token": fields.Char("Token"),
    }

    def authorize(self,ids,context={}):
        url="https://hotels.cloudbeds.com/api/v1.1/oauth?client_id=%s&redirect_uri=%s&response_type=code"%(CLIENT_ID,REDIRECT_URI)
        return {
            "next": {
                "type": "url",
                "url": url,
            }
        }

    def get_token(self,ids,context={}):
        print("get_token")
        obj=self.browse(ids[0])
        if not obj.oauth_code:
            raise Exception("Missing authorization code")
        url="https://hotels.cloudbeds.com/api/v1.1/access_token"
        params={
            "grant_type": "authorization_code",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI,
            "code": obj.oauth_code,
        }
        r=requests.post(url,data=params)
        r.raise_for_status()
        data=r.json()
        print("data",data)
        token=data["access_token"]
        print("TOKEN",token)
        obj.write({"token":token})

    def sync_cloudbeds(self, ids, context={}):
        obj=self.browse(ids[0])
        obj.sync_bookings(context=context)

    def sync_bookings(self,ids,context={}): 
        obj=self.browse(ids[0])
        if not obj.token:
            raise Exception("Missing token")
        url="https://hotels.cloudbeds.com/api/v1.1/getReservations"
        headers={
            "Authorization": "Bearer %s"%obj.token,
        }
        r=requests.get(url,headers=headers)
        r.raise_for_status()
        data=r.json()
        print("data",data)
        job_id=context.get("job_id")
        bookings=data["data"]
        for i,booking in enumerate(bookings):
            if job_id:
                if tasks.is_aborted(job_id):
                    return
                tasks.set_progress(job_id,i*100/len(bookings),"Importing reservation %s of %s."%(i+1,len(bookings)))
            number=booking["reservationID"]
            obj.sync_booking(number)

    def sync_booking(self,ids,number,context={}):
        obj=self.browse(ids[0])
        if not obj.token:
            raise Exception("Missing token")
        url="https://hotels.cloudbeds.com/api/v1.1/getReservation"
        params={
            "reservationID": number,
        }
        headers={
            "Authorization": "Bearer %s"%obj.token,
        }
        r=requests.get(url,params=params,headers=headers)
        r.raise_for_status()
        res=r.json()
        print("res",res)
        data=res["data"]
        main_guest_id=None
        for guest in data["guestList"].values():
            print("guest",guest)
            guest_vals={
                "code": guest["guestID"],
                "first_name": guest["guestFirstName"],
                "last_name": guest["guestLastName"],
                "email": guest["guestEmail"],
                "phone": guest["guestPhone"],
            }
            res=get_model("ht.guest").search([["code","=",guest["guestID"]]])
            if res:
                guest_id=res[0]
                get_model("ht.guest").write([guest_id],guest_vals)
            else:
                guest_id=get_model("ht.guest").create(guest_vals)
            if guest["isMainGuest"]:
                main_guest_id=guest_id
        print("main_guest_id",main_guest_id)
        booking_vals={
            "number": number,
            "guest_id": main_guest_id,
            "from_date": data["startDate"],
            "to_date": data["endDate"],
            "state": data["status"],
            "est_arrival_time": data.get("estimatedArrivalTime"),
            "assigns": [("delete_all",)],
        }
        res=get_model("ht.booking").search([["number","=",number]])
        if res:
            booking_id=res[0]
            get_model("ht.booking").write([booking_id],booking_vals)
        else:
            booking_id=get_model("ht.booking").create(booking_vals)
        for assign in data["assigned"]:
            print("assign",assign)
            res=get_model("ht.accom").search([["name","=",assign["roomName"]]])
            if res:
                accom_id=res[0]
            else:
                #raise Exception("Room not found: %s"%assign["roomName"])
                vals={
                    "name": assign["roomName"],
                }
                type_code=vals["name"].split("-")[0]
                res=get_model("ht.accom.type").search([["code","=",type_code]])
                if not res:
                    raise Exception("Room type not found: %s"%type_code)
                type_id=res[0]
                vals["accom_type_id"]=type_id
                accom_id=get_model("ht.accom").create(vals)
            accom=get_model("ht.accom").browse(accom_id)
            assign_vals={
                "booking_id": booking_id,
                "from_date": assign["startDate"],
                "to_date": assign["endDate"],
                "accom_type_id": accom.accom_type_id.id,
                "accom_id": accom_id,
                "amount": assign["roomTotal"],
            }
            get_model("ht.assign").create(assign_vals)
        booking=get_model("ht.booking").browse(booking_id)
        if not booking.invoice_id:
            booking.copy_to_invoice()

Sync.register()
