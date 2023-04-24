from netforce.model import Model,fields

class Settings(Model):
    _inherit="settings"
    _fields={
        "pos_contact_id": fields.Many2One("contact","POS Contact",multi_company=True),
        "pos_sale_account_id": fields.Many2One("account.account","POS Sales Account",multi_company=True),
        "pos_location_id": fields.Many2One("stock.location","POS Location",multi_company=True),
        "pos_bills": fields.Char("Bill Amounts"),
        "pos_table_required": fields.Boolean("POS Table Required"),
        "pos_logo": fields.File("POS Logo"),
        "pos_save_receipts": fields.Boolean("Save POS Receipts"),
        "pos_pay_method_id": fields.Many2One("payment.method","POS Payment Method",multi_company=True),
        "pos_lock_date": fields.Date("POS Lock Date"),
    }

Settings.register()
