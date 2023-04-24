from netforce.model import Model,fields,get_model
from netforce import utils
from netforce import access
from netforce_report import render_template_hbs
import math
import string
import base64
import time
import random
try:
    import escpos.printer
except:
    print("WARNING: failed to import escpos")
try:
    from PIL import Image, ImageFont, ImageOps, ImageDraw
except:
    print("WARNING: failed to import PIL")

printable = string.ascii_letters + string.digits + string.punctuation + ' '

def hex_escape(s):
    return ''.join(c if c in printable else r'\x{0:02x}'.format(ord(c)) for c in s)

def _get_pay_amounts(amt,bills):
    if not bills:
        return []
    bill_amt=bills[0]
    n=int(math.ceil(float(amt)/float(bill_amt)))
    amounts=[n*bill_amt]
    amounts+=_get_pay_amounts(amt,bills[1:])
    amounts=list(set(amounts))
    amounts.sort()
    #if bill_amt>=amt:
    #    rem_amounts=get_amounts(amt-bill_amt,bills[:-1])
    #    amounts+=[a+bill_amt for a in rem_amounts]
    return amounts

class Cart(Model):
    _inherit="ecom2.cart"
    _fields={
        "pos_pay_amounts": fields.Json("Pay Amounts",function="get_pay_amounts"),
        "pos_table_id": fields.Many2One("pos.table","Table"),
    }

    def confirm_pos(self,ids,context={}):
        company_id=access.get_active_company()
        settings=get_model("settings").browse(1)
        pay_method_id=context.get("pay_method_id")
        if not pay_method_id:
            pay_method_id=settings.pos_pay_method_id.id
            context["pay_method_id"]=pay_method_id
        if not pay_method_id:
            raise Exception("Missing payment method")
        obj=self.browse(ids)[0]
        if obj.state not in ("draft","hold"):
            raise Exception("Invalid cart status: %s"%obj.state)
        obj.write({"company_id":company_id})
        if not obj.contact_id:    
            settings=get_model("settings").browse(1)
            if not settings.pos_contact_id:
                raise Exception("Missing POS contact in settings")
            obj.write({"customer_id": settings.pos_contact_id.id})
        if settings.pos_table_required and not obj.pos_table_id:
            raise Exception("Missing queue")
        res=obj.confirm(context={"location_id":settings.pos_location_id.id})
        sale_id=res["sale_id"]
        sale=get_model("sale.order").browse(sale_id)
        sale.write({"due_date":sale.date})
        res=sale.copy_to_invoice()
        inv_id=res["invoice_id"]
        inv=get_model("account.invoice").browse(inv_id)
        inv.write({"due_date":inv.date})
        for line in inv.lines:
            if not line.account_id:
                if not settings.pos_sale_account_id:
                    raise Exception("Missing POS sales account")
                line.write({"account_id": settings.pos_sale_account_id.id})
        inv.post()
        res=sale.copy_to_picking()
        pick_id=res["picking_id"]
        pick=get_model("stock.picking").browse(pick_id)
        pick.set_done()
        sale.payment_received(context=context)
        res=obj.get_pos_receipt()
        print_data=res["data"]
        return {
            "sale_id": sale_id,
            "sale_number": sale.number,
            "print_data": print_data,
        }

    def pos_park(self,ids,context={}):
        settings=get_model("settings").browse(1)
        obj=self.browse(ids)[0]
        if not obj.contact_id:    
            settings=get_model("settings").browse(1)
            if not settings.pos_contact_id:
                raise Exception("Missing POS contact")
            obj.write({"customer_id": settings.pos_contact_id.id})
        res=obj.confirm(context={"state":"draft","location_id":settings.pos_location_id.id})
        sale_id=res["sale_id"]
        sale=get_model("sale.order").browse(sale_id)
        return {
            "sale_id": sale_id,
            "sale_number": sale.number,
        }

    def get_pay_amounts(self,ids,context={}):
        settings=get_model("settings").browse(1)
        bills=[int(x) for x in settings.pos_bills.split(",")] if settings.pos_bills else []
        vals={}
        for obj in self.browse(ids):
            vals[obj.id]=[obj.amount_total]+_get_pay_amounts(obj.amount_total,bills)
        return vals

    def pos_payment_received(self,ids,context={}):
        settings=get_model("settings").browse(1)
        obj=self.browse(ids[0])
        if not obj.contact_id:    
            settings=get_model("settings").browse(1)
            if not settings.pos_contact_id:
                raise Exception("Missing POS contact")
            obj.write({"customer_id": settings.pos_contact_id.id})
        res=obj.confirm(context={"location_id":settings.pos_location_id.id})
        sale_id=res["sale_id"]
        sale=get_model("sale.order").browse(sale_id)
        sale.write({"due_date":sale.date})
        res=sale.copy_to_invoice()
        inv_id=res["invoice_id"]
        inv=get_model("account.invoice").browse(inv_id)
        inv.write({"due_date":inv.date})
        for line in inv.lines:
            if not line.account_id:
                if not settings.pos_sale_account_id:
                    raise Exception("Missing POS sales account")
                line.write({"account_id": settings.pos_sale_account_id.id})
        inv.post()
        res=sale.copy_to_picking()
        pick_id=res["picking_id"]
        pick=get_model("stock.picking").browse(pick_id)
        pick.set_done()
        sale.payment_received(context=context)
        return {
            "flash": "Order paid: %s"%sale.number,
            "next": {
                "name": "pos_product_m",
            },
        }

    def pos_hold(self,ids,context={}):
        settings=get_model("settings").browse(1)
        obj=self.browse(ids[0])
        if settings.pos_table_required and not obj.pos_table_id:
            raise Exception("Missing table")
        obj.write({"state":"hold"})

    def pos_cancel(self,ids,context={}):
        obj=self.browse(ids[0])
        if obj.state=="confirmed":
            return
        obj.write({"state":"canceled"})

    def pos_restore(self,ids,context={}):
        obj=self.browse(ids[0])
        obj.write({"state":"draft"})

    def get_pos_receipt(self,ids,context={}):
        settings=get_model("settings").browse(1)
        obj=self.browse(ids[0])
        res=get_model("report.template").search([["name","=","pos_receipt"]])
        if not res:
            raise Exception("Template not found: pos_receipt")
        tmpl_id=res[0]
        tmpl=get_model("report.template").browse(tmpl_id)
        body=tmpl.body
        fields=["number","date","amount_total","pay_amount","change_amount","lines.product_id.name","lines.product_id.code","lines.qty","lines.unit_price","lines.amount","customer_id.name","customer_id.default_address_id.address","customer_id.default_address_id.address2","customer_id.default_address_id.postal_code","customer_id.default_address_id.city","customer_id.tax_no","pos_table_id.name"]
        res=get_model("ecom2.cart").read_path([obj.id],fields)
        data=res[0]
        data["print_time"]=time.strftime("%Y-%m-%d %H:%M:%S")
        out_str=render_template_hbs(body,data)
        print("!"*80)
        print("out",hex_escape(out_str))
        #out_bin=out_str.encode("tis-620")
        #out_bin=out_str.encode("cp874")
        #out_bin=out_str.encode("iso8859_11")
        #out_bin=_thai_conv_escp(out_bin)
        #out_bin=b"TEST\n===\n\xa1\xa1\xa1\n===\n"
        #out_bin=b"\x1bt\x15\x1dP\x40\x40TEST7\n===\n\xa1 \xa1 \xa1\x1b$\x00\x01HELLO\n===\n\n"
        #out_bin=open("/home/datrus/escpos/print.bin","rb").read()
        font_path="/usr/share/fonts/truetype/tlwg/TlwgMono-Bold.ttf"
        width = 384 
        if settings.pos_logo:
            path=utils.get_file_path(settings.pos_logo)
            logo_img=Image.open(path,"r")
            logo_h=logo_img.size[1]
        else:
            logo_img=None
            logo_h=0
        lines=out_str.split("\n")
        height=len(lines)*24
        height+=logo_h
        font=ImageFont.truetype(font_path,24)
        print("width",width)
        print("height",height)
        img=Image.new("RGB",(width,height))
        img.paste("#fff")
        if logo_img:
            img.paste(logo_img,(0,0))
        draw=ImageDraw.Draw(img)
        draw.fontmode="1"
        for i,line in enumerate(lines):
            if not line:
                continue
            filt_lines=utils.i18n_filter_line(line)
            for fl in filt_lines:
                draw.text((0,logo_h+i*24),fl,font=font,fill="#000")
        if settings.pos_save_receipts:
            fname="pos-receipt-%s.png"%random.randint(0,999999999)
            img_path = utils.get_file_path(fname)
            img.save(img_path)
            vals={
                "file": fname,
                "related_id": "ecom2.cart,%s"%obj.id,
            }
            get_model("document").create(vals)
        
        p=escpos.printer.Dummy()
        p.image(img,impl="bitImageColumn")
        p.cut()
        out_bin=p.output

        data=base64.b64encode(out_bin).decode()
        print("data",data)
        return {
            "data": data, 
        }

    def set_table(self,ids,table_id,context={}):
        obj=self.browse(ids[0])
        obj.write({"pos_table_id":table_id})

Cart.register()
