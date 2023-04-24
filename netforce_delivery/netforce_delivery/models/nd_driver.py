from netforce.model import Model,fields,get_model
from netforce import database
import time

class Driver(Model):
    _name="nd.driver"
    _string="Driver"
    _fields={
        "name": fields.Char("Driver Name"),
        "mobile": fields.Char("Mobile"),
        "accept_driver": fields.Boolean("Accepted By Driver"),
        "accept_account": fields.Boolean("Accepted By Employer"),
        "sequence": fields.Integer("Sequence"),
        "routes": fields.One2Many("nd.route","driver_id","Routes"),
        "num_routes": fields.Integer("Number Of Routes",function="get_num_routes",function_multi=True),
        "rounds": fields.One2Many("nd.round","driver_id","Rounds"),
        "num_rounds": fields.Integer("# Rounds",function="get_num_rounds"),
        "jobs": fields.One2Many("nd.job","driver_id","Jobs"),
        "events": fields.One2Many("nd.event","driver_id","Events"),
        "date_register": fields.DateTime("Date Registered"),
        "coords": fields.Char("Coordinates"),
        "bat_level": fields.Integer("Battery Level"),
        "track_id": fields.Many2One("account.track.categ","Tracking Account"),
    }
    _order="sequence,id"

    def get_num_rounds(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            vals[obj.id]=len(obj.rounds)
        return vals

    def set_sequence(self,ids,context={}):
        print("Driver.set_sequence",ids)
        seq=1
        for obj in self.browse(ids):
            obj.write({"sequence":seq})
            seq+=1

    def register_driver(self,mobile,name,context={}):
        res=self.search([["mobile","=",mobile],["account_id","=",None]]) # XXX
        if res:
            driver_id=res[0]
        else:
            vals={
                "mobile": mobile,
                "name": name,
                "account_id": None,
            }
            driver_id=self.create(vals)
        driver=self.browse(driver_id)
        driver.write({"name":name,"date_register":time.strftime("%Y-%m-%d %H:%M:%S")})
        return {
            "driver_id": driver_id,
        }

Driver.register()
