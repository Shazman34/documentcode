from netforce.model import Model,fields,get_model
import time

class Company(Model):
    _name="l2g.company"
    _string="Company"
    _fields={
        "name": fields.Char("Company Name",required=True),
        "customers": fields.One2Many("l2g.customer","company_id","Customers"),
        "num_customers": fields.Integer("# Customers",function="get_num_customers"),
        "balance": fields.Decimal("Payable Balance",function="get_balance"),
        "contact_id": fields.Many2One("contact","Contact"),
    }
    _order="name"

    def get_num_customers(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            vals[obj.id]=len(obj.customers)
        return vals

    def get_balance(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            contact=obj.contact_id
            if contact and contact.track_id:
                bal=contact.track_id.balance
            else:
                bal=0
            vals[obj.id]=bal
        return vals

    def copy_to_contact(self,ids,context={}):
        for obj in self.browse(ids):
            if not obj.contact_id:
                vals={
                    "type": "org",
                    "name": obj.name,
                }
                contact_id=get_model("contact").create(vals)
                obj.write({"contact_id": contact_id})

Company.register()
