from netforce.model import Model,fields,get_model
import time

class Doc(Model):
    _name="ht.doc"
    _string="Document"
    _name_field="number"
    _fields={
        "type": fields.Selection([["driver_license","Driver's License"],["student_id","Student ID"],["passport","Passport"],["dni","DNI"],["nie","NIE"]],"Type Of Document",required=True),
        "number": fields.Char("Document Number",required=True),
        "issue_date": fields.Date("Document Issue Date"),
        "issue_country_id": fields.Many2One("country","Document Issuing Country"),
        "expire_date": fields.Date("Document Expiration Date"),
        "file": fields.File("File"),
        "guest_id": fields.Many2One("ht.guest","Guest"),
        "booking_id": fields.Many2One("ht.booking","Reservation"),
    }

Doc.register()
