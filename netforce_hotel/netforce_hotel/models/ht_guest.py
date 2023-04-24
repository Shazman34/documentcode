from netforce.model import Model,fields,get_model
import time

class Guest(Model):
    _name="ht.guest"
    _string="Guest"
    _fields={
        "code": fields.Char("Guest ID",search=True,required=True),
        "first_name": fields.Char("First Name",required=True,search=True),
        "last_name": fields.Char("Last Name",required=True,search=True),
        "email": fields.Char("Email",search=True),
        "phone": fields.Char("Phone",search=True),
        "birth_date": fields.Date("Date of Birth",search=True),
        "picture": fields.File("Picture"),
        "addresses": fields.One2Many("address","related_id","Addresses"),
        "docs": fields.One2Many("ht.doc","guest_id","Documents"),
        "categ_id": fields.Many2One("ht.guest.categ","Guest Category"),
        "contact_id": fields.Many2One("contact","Contact"),
    }
    _order="first_name,last_name"

    def name_get(self,ids,context={}):
        res=[]
        for obj in self.browse(ids):
            name="%s %s"%(obj.first_name,obj.last_name)
            res.append([obj.id,name])
        return res

    def copy_to_contact(self,ids,context={}):
        n=0
        for obj in self.browse(ids):
            if obj.contact_id:
                continue
            vals={
                "first_name": obj.first_name,
                "last_name": obj.last_name,
                "email": obj.email,
                "phone": obj.phone,
                "birth_date": obj.birth_date,
            }
            contact_id=get_model("contact").create(vals)
            obj.write({"contact_id": contact_id})
            n+=1
        return {
            "alert": "%d contacts created"%n,
        }

Guest.register()
