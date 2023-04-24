from netforce.model import Model,fields,get_model
from netforce import access
from datetime import *
from decimal import *
import time

class SaleModif(Model):
    _inherit="sale.modif"

    def do_update_related(self,ids,context={}):
        company_id=access.get_active_company()
        access.set_active_user(1)
        res=get_model("company").search([["code","=","KFF"]])
        if not res:
            raise Exception("Company code not found: KFF")
        kff_company_id=res[0]
        obj=self.browse(ids[0])
        sale=obj.order_id
        prod=obj.product_id
        if obj.type=="add_prod":
            if not sale.sale_orders:
                raise Exception("KFF sales order not found")
            sale2=sale.sale_orders[0]
            vals={
                "order_id": sale2.id,
                "product_id": prod.id,
                "description": "Labor for %s"%prod.name,
                "qty": obj.qty,
                "uom_id": prod.uom_id.id,
                "unit_price": obj.labor_cost,
                "location_id": obj.location_id.id,
            }
            line_id=get_model("sale.order.line").create(vals)
            sale2.function_store()

            res=get_model("bom").search([["product_id","=",prod.id]])
            if not res:
                raise Exception("BoM not found for product '%s'" % prod.name)
            bom_id = res[0]
            bom = get_model("bom").browse(bom_id)
            loc_id = bom.location_id.id
            if not loc_id:
                raise Exception("Missing FG location in BoM %s" % bom.number)
            loc_prod_id = bom.production_location_id.id
            if not loc_prod_id:
                raise Exception("Missing production location in BoM %s" % bom.number)
            uom = prod.uom_id

            order_vals = {
                "company_id": kff_company_id,
                "product_id": prod.id,
                "qty_planned": obj.qty,
                "uom_id": uom.id,
                "bom_id": bom_id,
                "production_location_id": loc_prod_id,
                "location_id": loc_id,
                "order_date": time.strftime("%Y-%m-%d"),
                "due_date": obj.due_date,
                "state": "draft",
                "sale_id": sale2.id,
                "ref": sale2.number,
                "customer_id": sale.contact_id.id,
            }
            access.set_active_company(kff_company_id)
            mfg_order_id = get_model("production.order").create(order_vals)
            get_model("production.order").create_components([mfg_order_id])
            get_model("production.order").create_operations([mfg_order_id])
            mfg_order=get_model("production.order").browse(mfg_order_id)
        elif obj.type=="change_qty":
            prod_id=obj.product_id.id
            if not prod_id:
                raise Exception("Missing product")
            if not obj.qty:
                raise Exception("Missing qty")
            if not sale.sale_orders:
                raise Exception("KFF sales order not found")
            sale2=sale.sale_orders[0]
            for line in sale2.lines:
                if line.product_id.id==prod_id:
                    line.write({"qty":obj.qty})
            sale2.function_store()
            for mo in sale2.production_orders:
                if mo.product_id.id==prod_id:
                    mo.write({"qty_planned":obj.qty})

SaleModif.register()
