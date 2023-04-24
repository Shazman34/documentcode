from netforce.model import Model,fields,get_model
import time
import googlemaps

API_KEY="AIzaSyBI3HlDzSbV1MPwIVFzQFqduVwB8bidsO8"

class GetAddr(Model):
    _name="l2g.get.addr"
    _fields={
        "booking_id": fields.Many2One("l2g.booking","Booking",required=True),
        "location": fields.Char("Location",required=True),
        "type": fields.Selection([["from","From Location"],["to","To Location"]],"Type",required=True),
    }

    def set_addr(self,ids,context={}):
        print("set_addr",ids)
        obj=self.browse(ids[0])
        client=googlemaps.Client(key=API_KEY)
        loc=obj.location
        res=client.geocode(loc)
        print("res",res)

GetAddr.register()
