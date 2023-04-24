from netforce.model import Model,fields,get_model
from netforce import access
from datetime import *
import time

class Booking(Model):
    _name="ht.booking"
    _string="Reservation"
    _name_field="number"
    _fields={
        "number": fields.Char("Reservation ID",required=True,search=True),
        "guest_id": fields.Many2One("ht.guest","Main Guest",required=True,search=True),
        "from_date": fields.Date("Check-In Date",required=True),
        "to_date": fields.Date("Check-Out Date",required=True),
        "num_nights": fields.Integer("Number Of Nights",function="get_num_nights"),
        "date": fields.Date("Reservation Date",required=True),
        "num_guests": fields.Integer("Num Guests"),
        "source_id": fields.Many2One("ht.source","Source"),
        "assigns": fields.One2Many("ht.assign","booking_id","Accomodations"),
        "docs": fields.One2Many("ht.doc","booking_id","Documents"),
        "state": fields.Selection([["in_progress","Pending Confirmation"],["confirmed","Confirmed"],["checked_in","Checked In"],["checked_out","Checked Out"],["not_confirmed","Not Confirmed"],["canceled","Canceled"],["no_show","No Show"]],"Status",required=True,search=True),
        "amount_total": fields.Decimal("Total Amount",function="get_amount_total"),
        "invoice_id": fields.Many2One("account.invoice","Invoice"),
        "payment_id": fields.Many2One("account.payment","Payment"),
        "est_arrival_time": fields.Char("Est. Arrival Time"),
        "amount_paid": fields.Decimal("Paid Amount"),
    }
    _order="from_date desc,id desc"

    def _get_number(self, context={}):
        seq_id = get_model("sequence").find_sequence(name="ht_booking",context=context)
        if not seq_id:
            raise Exception("Missing number sequence for bookings")
        while 1:
            num = get_model("sequence").get_next_number(seq_id, context=context)
            if not num:
                return None
            user_id = access.get_active_user()
            access.set_active_user(1)
            res = self.search([["number", "=", num]])
            access.set_active_user(user_id)
            if not res:
                return num
            get_model("sequence").increment_number(seq_id, context=context)

    _defaults={
        "number": _get_number,
        "date": lambda *a: time.strftime("%Y-%m-%d"),
        "state": "in_progress",
    }

    def get_num_nights(self, ids, context={}):
        vals={}
        for obj in self.browse(ids):
            if obj.from_date and obj.to_date:
                d0=datetime.strptime(obj.from_date,"%Y-%m-%d")
                d1=datetime.strptime(obj.to_date,"%Y-%m-%d")
                vals[obj.id]=(d1-d0).days
        return vals

    def get_amount_total(self, ids, context={}):
        vals={}
        for obj in self.browse(ids):
            total=0
            for assign in obj.assigns:
                total+=assign.amount or 0
            vals[obj.id]=total
        return vals

    def copy_to_invoice(self, ids, context={}):
        print("booking.copy_to_invoice",ids)
        access.set_active_company(4)
        n=0
        for obj in self.browse(ids):
            if obj.invoice_id:
                continue
            obj.guest_id.copy_to_contact()
            obj=obj.browse()[0]
            inv_vals = {
                "type": "out",
                "inv_type": "invoice",
                "contact_id": obj.guest_id.contact_id.id,
                "lines": [],
                "ref": obj.number,
            }
            for assign in obj.assigns:
                prod=assign.accom_type_id.product_id
                if not prod:
                    raise Exception("Missing product for accomodation type %s"%assign.accom_type_id.name)
                if assign.amount is None:
                    raise Exception("Missing amount for %s / %s"%(obj.number,assign.accom_type_id.name))
                line_vals = {
                    "product_id": prod.id,
                    "description": "%s (%s -> %s)"%(assign.accom_type_id.name,assign.date_from,assign.date_to),
                    "qty": 1,
                    "uom_id": prod.uom_id.id,
                    "unit_price": assign.amount,
                    "account_id": prod.sale_account_id.id,
                    "tax_id": prod.sale_tax_id.id,
                    "amount": assign.amount,
                }
                inv_vals["lines"].append(("create", line_vals))
            if not inv_vals["lines"]:
                continue
            inv_id = get_model("account.invoice").create(inv_vals, {"type": "out", "inv_type": "invoice"})
            obj.write({"invoice_id":inv_id})
            n+=1
        return {
            "flash": "%s invoices created"%n,
        }

    def confirm(self,ids,context={}):
        obj=self.browse(ids[0])
        obj.write({"state":"confirmed"})

    def check_in(self,ids,context={}):
        obj=self.browse(ids[0])
        obj.write({"state":"checked_in"})

    def check_out(self,ids,context={}):
        obj=self.browse(ids[0])
        obj.write({"state":"checked_out"})

Booking.register()
