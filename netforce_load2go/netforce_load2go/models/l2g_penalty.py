from netforce.model import Model,fields,get_model
import time

class Penalty(Model):
    _name="l2g.penalty"
    _string="Additional Charge"
    _fields={
        "type": fields.Selection([["penalty","Penalty"],["levy","Levy"],["customs","Customs Clearance"]],"Type",required=True),
        "name": fields.Char("Name",required=True),
        "from_country_id": fields.Many2One("country","From Country"),
        "to_country_id": fields.Many2One("country","To Country"),
        "from_addr": fields.Char("From Address"),
        "to_addr": fields.Char("To Address"),
        "fee": fields.Decimal("Fee",required=True),
        "booking_id": fields.Many2One("l2g.booking","Booking",store=False,function_search="search_booking"),
    }

    def search_booking(self,clause,context={}):
        booking_id=clause[2]
        booking=get_model("l2g.booking").browse(booking_id)
        ids=[]
        for obj in self.search_browse([]):
            if obj.from_addr and obj.from_addr!=booking.load_addr:
                continue
            if obj.to_addr and obj.to_addr!=booking.delivery_addr:
                continue
            if obj.from_country_id and obj.from_country_id.id!=booking.from_country_id.id:
                continue
            if obj.to_country_id and obj.to_country_id.id!=booking.to_country_id.id:
                continue
            ids.append(obj.id)
        return ["id","in",ids]

Penalty.register()
