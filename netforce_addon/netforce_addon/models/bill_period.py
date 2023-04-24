from netforce.model import Model,fields

class Period(Model):
    _name="bill.period"
    _fields={
        "date_from": fields.Date("From Date",required=True),
        "date_to": fields.Date("To Date",required=True),
        "amount_bill": fields.Decimal("Bill Amount",required=True),
        "amount_paid": fields.Decimal("Paid Amount"),
    }
    _order="date_from desc"

Period.register()
