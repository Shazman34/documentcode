from netforce.model import Model,fields,get_model
import time

class Trans(Model):
    _name="l2g.trans"
    _string="Transaction"
    _fields={
        "time": fields.DateTime("Time",required=True),
        "driver_id": fields.Many2One("l2g.driver","Driver"),
        "customer_id": fields.Many2One("l2g.customer","Customer"),
        "amount": fields.Decimal("Transaction Amount",required=True),
        "balance": fields.Decimal("Wallet Balance",readonly=True),
        "description": fields.Text("Description",required=True),
    }
    _defaults={
        "time": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    _order="time desc,id desc"

    def create(self,vals,**kw):
        new_id=super().create(vals,**kw)
        obj=self.browse(new_id)
        if obj.driver_id:
            obj.driver_id.update_balances()
        elif obj.customer_id:
            obj.customer_id.update_balances()
        return new_id

Trans.register()
