from netforce.model import Model,fields,get_model
from netforce import access
from datetime import *
from decimal import *
import time

class Order(Model):
    _inherit="sale.order"
    _fields={
        "supplier_type": fields.Selection([["internal","Internal (KingFreshFarm)"],["external","Other Supplier"]],"Supplier Type"),
    }

    def confirm(self,ids,context={}):
        super().confirm(ids,context=context)
        obj=self.browse(ids[0])
        if obj.company_id.code=="TG":
            obj.tg_make_freight_inv()
            mo_ids=obj.tg_make_mo()["order_ids"]
            get_model("production.order").tg_make_po_packing(mo_ids)
            get_model("production.order").tg_make_po_fruit(mo_ids)

    def tg_make_freight_inv(self, ids, context={}):
        print("sale.copy_to_invoice_tg",ids)
        res=get_model("sequence").search([["name","=","FINV"]])
        if not res:
            raise Exception("Sequence not found: FINV")
        seq_id=res[0]
        inv_vals=None
        for obj in self.browse(ids):
            if obj.state!="confirmed":
                raise Exception("Sales order must be confirmed first.")
            if inv_vals is None:
                inv_vals = {
                    "type": "out",
                    "inv_type": "invoice",
                    "contact_id": obj.contact_id.id,
                    "bill_address_id": obj.bill_address_id.id,
                    "currency_id": obj.currency_id.id,
                    "tax_type": obj.tax_type,
                    "pay_method_id": obj.pay_method_id.id,
                    "lines": [],
                    "company_id": obj.company_id.id,
                    "pay_term_id": obj.pay_term_id.id,
                    "ref": "FREIGHT %s"%obj.number,
                    "date": obj.due_date or time.strftime("%Y-%m-%d"),
                    "sequence_id": seq_id,
                }
                if obj.pay_term_id and obj.pay_term_id.days:
                    d=datetime.strptime(inv_vals["date"],"%Y-%m-%d")
                    d+=timedelta(days=obj.pay_term_id.days)
                    inv_vals["due_date"]=d.strftime("%Y-%m-%d")
                access.set_active_company(obj.company_id.id) # XXX
            else:
                if obj.contact_id.id!=inv_vals["contact_id"]:
                    raise Exception("Sales orders are for different customers")
                if obj.bill_address_id.id!=inv_vals["bill_address_id"]:
                    raise Exception("Sales orders have different billing address")
                if obj.currency_id.id!=inv_vals["currency_id"]:
                    raise Exception("Sales orders have different currencies")
                if obj.tax_type!=inv_vals["tax_type"]:
                    raise Exception("Sales orders have different tax types")
                if obj.pay_method_id.id!=inv_vals["pay_method_id"]:
                    raise Exception("Sales orders have different payment methods")
                if obj.company_id.id!=inv_vals["company_id"]:
                    raise Exception("Sales orders are in different companies")
            for line in obj.lines:
                if not line.unit_price:
                    continue
                prod = line.product_id
                #remain_qty = line.qty - line.qty_invoiced
                remain_qty=int(line.qty*Decimal(1.2)) # XXX
                if remain_qty <= 0:
                    continue
                sale_acc_id=None
                if prod:
                    sale_acc_id=prod.sale_account_id.id
                    if not sale_acc_id and prod.parent_id:
                        sale_acc_id=prod.parent_id.sale_account_id.id
                    if not sale_acc_id and prod.categ_id and prod.categ_id.sale_account_id:
                        sale_acc_id=prod.categ_id.sale_account_id.id
                line_vals = {
                    "product_id": prod.id,
                    "description": line.description,
                    "qty": remain_qty,
                    "uom_id": line.uom_id.id,
                    "unit_price": line.unit_price,
                    "discount": line.discount,
                    "discount_amount": line.discount_amount,
                    "account_id": sale_acc_id,
                    "tax_id": line.tax_id.id,
                    "amount": remain_qty*line.unit_price*(1-(line.discount or Decimal(0))/100)-(line.discount_amount or Decimal(0)),
                    "related_id": "sale.order,%d"%obj.id,
                }
                inv_vals["lines"].append(("create", line_vals))
                if line.promotion_amount:
                    prom_acc_id=None
                    if prod:
                        prom_acc_id=prod.sale_promotion_account_id.id
                        if not prom_acc_id and prod.parent_id:
                            prom_acc_id=prod.parent_id.sale_promotion_account_id.id
                    if not prom_acc_id:
                        prom_acc_id=sale_acc_id
                    line_vals = {
                        "product_id": prod.id,
                        "description": "Promotion on product %s"%prod.code,
                        "account_id": prom_acc_id,
                        "tax_id": line.tax_id.id,
                        "amount": -line.promotion_amount,
                    }
                    inv_vals["lines"].append(("create", line_vals))
            for line in obj.used_promotions:
                if line.product_id or line.percent:
                    continue
                prom=line.promotion_id
                prod = prom.product_id
                line_vals = {
                    "product_id": prod.id,
                    "description": prom.name,
                    "account_id": prod and prod.sale_account_id.id or None,
                    "tax_id": prod and prod.sale_tax_id.id or None,
                    "amount": -line.amount,
                }
                inv_vals["lines"].append(("create", line_vals))
        if not inv_vals or not inv_vals["lines"]:
            raise Exception("Nothing to invoice")
        inv_id = get_model("account.invoice").create(inv_vals, {"type": "out", "inv_type": "invoice", "sequence_id": seq_id})
        inv=get_model("account.invoice").browse(inv_id)
        return {
            "next": {
                "name": "view_invoice",
                "active_id": inv_id,
            },
            "flash": "Invoice %s created from sales order" % inv.number,
            "invoice_id": inv_id,
        }

    def tg_make_mo(self, ids, context={}):
        company_id=access.get_active_company()
        access.set_active_user(1)
        res=get_model("company").search([["code","=","KFF"]])
        if not res:
            raise Exception("Company code not found: KFF")
        kff_company_id=res[0]
        order_ids = []
        mfg_orders = {}
        for obj in self.browse(ids):
            for line in obj.lines:
                prod = line.product_id
                if not prod:
                    continue
                #if prod.procure_method!="mto" or prod.supply_method != "production":
                #    continue
                due_date=line.due_date or obj.due_date
                if not due_date:
                    raise Exception("Missing shipping date in sales order %s"%obj.number)
                if context.get("due_date") and due_date!=context["due_date"]:
                    continue
                if line.production_id:
                    raise Exception("Production order already created for sales order %s, product %s"%(obj.number,prod.code))
                k=(prod.id,due_date)
                mfg_orders.setdefault(k,[]).append(line.id)
        for (prod_id,due_date),sale_line_ids in mfg_orders.items():
            prod=get_model("product").browse(prod_id)
            res=get_model("bom").search([["product_id","=",prod.id]]) # TODO: select bom in separate function
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
            mfg_qty=0
            for line in get_model("sale.order.line").browse(sale_line_ids):
                if line.qty_stock:
                    qty = line.qty_stock
                else:
                    qty = get_model("uom").convert(line.qty, line.uom_id.id, uom.id)
                mfg_qty+=qty
            mfg_date=(datetime.strptime(due_date,"%Y-%m-%d")-timedelta(days=prod.mfg_lead_time or 0)).strftime("%Y-%m-%d")
            sale_id=ids[0] # XXX
            sale=get_model("sale.order").browse(sale_id)
            order_vals = {
                "company_id": kff_company_id,
                "product_id": prod.id,
                "qty_planned": mfg_qty,
                "uom_id": uom.id,
                "bom_id": bom_id,
                "production_location_id": loc_prod_id,
                "location_id": loc_id,
                "order_date": mfg_date,
                "due_date": due_date,
                "state": "draft",
                "sale_id": sale_id, # XXX
                "ref": sale.number,
                "customer_id": obj.contact_id.id, # XXX
            }
            access.set_active_company(kff_company_id)
            order_id = get_model("production.order").create(order_vals)
            get_model("production.order").create_components([order_id])
            get_model("production.order").create_operations([order_id])
            order=get_model("production.order").browse(order_id)
            #access.set_active_company(kff_company_id) # XXX
            #res=order.copy_to_purchase()
            #purch_ids=res.get("purchase_ids",[])
            #for purch in get_model("purchase.order").browse(purch_ids):
            #    purch.write({"ref":"%s RM"%obj.number,"related_id":"sale.order,%s"%obj.id})
            order_ids.append(order_id)
            access.set_active_company(company_id)
            get_model("sale.order.line").write(sale_line_ids,{"production_id":order_id})
        if not order_ids:
            return {
                "flash": "No production orders to create",
            }
        return {
            "flash": "Production orders created successfully",
            "order_ids": order_ids,
        }

    def tg_make_pick_out(self,ids,context={}):
        obj=self.browse(ids[0])
        res=get_model("company").search([["code","=","TG"]])
        if not res:
            raise Exception("Company code not found: TG")
        tg_company_id=res[0]
        pick_vals = {
            "type": "out",
            "contact_id": obj.contact_id.id,
            "lines": [],
            "company_id": obj.company_id.id,
            "ref": "SHIP %s"%obj.number,
            "related_id": "sale.order,%s"%obj.id,
            "company_id": tg_company_id,
        }
        res = get_model("stock.location").search([["type", "=", "customer"]])
        if not res:
            raise Exception("Customer location not found")
        cust_loc_id = res[0]
        for line in obj.lines:
            prod=line.product_id
            qty_received=line.qty_produced or 0
            line_vals = {
                "product_id": prod.id,
                "qty": qty_received,
                "uom_id": line.uom_id.id,
                "location_from_id": line.location_id.id,
                "location_to_id": cust_loc_id,
                "related_id": "sale.order,%s"%obj.id,
            }
            pick_vals["lines"].append(("create",line_vals))
        if not pick_vals["lines"]:
            raise Exception("Nothing to invoice")
        access.set_active_company(tg_company_id)
        pick_id = get_model("stock.picking").create(pick_vals, {"pick_type": "out"})
        pick=get_model("stock.picking").browse(pick_id)
        return {
            "next": {
                "name": "view_picking",
                "active_id": pick_id,
            },
            "flash": "Goods Issue %s created from sales order" % pick.number,
            "picking_id": pick_id,
        }

    def kff_make_labor_inv(self,ids,context={}):
        obj=self.browse(ids[0])
        res=get_model("company").search([["code","=","KFF"]])
        if not res:
            raise Exception("Company code not found: KFF")
        kff_company_id=res[0]
        res=get_model("contact").search([["code","=","TG"]])
        if not res:
            raise Exception("Supplier code not found: TG")
        contact_id=res[0]
        inv_vals = {
            "type": "out",
            "inv_type": "invoice",
            "contact_id": contact_id,
            "lines": [],
            "company_id": obj.company_id.id,
            "ref": "LABOR %s"%obj.number,
            "related_id": "sale.order,%s"%obj.id,
            "company_id": kff_company_id,
        }
        for line in obj.lines:
            prod = line.product_id
            if not line.qty_produced:
                continue
            line_vals = {
                "product_id": prod.id,
                "description": prod.description or "/",
                "qty": line.qty_produced,
                "uom_id": line.uom_id.id,
                "unit_price": line.unit_price,
                "account_id": prod.sale_account_id.id,
                "tax_id": prod.sale_tax_id.id,
                "related_id": "sale.order,%s"%obj.id,
                "discount": line.discount,
                "discount_amount": line.discount_amount,
            }
            line_vals["amount"]=line_vals["qty"]*line_vals["unit_price"]
            inv_vals["lines"].append(("create",line_vals))
        if not inv_vals["lines"]:
            raise Exception("Nothing to invoice")
        access.set_active_company(kff_company_id)
        inv_id = get_model("account.invoice").create(inv_vals, {"type": "out", "inv_type": "invoice"})
        inv=get_model("account.invoice").browse(inv_id)
        inv.copy_to_cust_supp_invoice()
        return {
            "next": {
                "name": "view_invoice",
                "active_id": inv_id,
            },
            "flash": "Invoice %s created from production orders" % inv.number,
            "invoice_id": inv_id,
        }

    def tg_make_cust_inv(self,ids,context={}):
        obj=self.browse(ids[0])
        freight_inv=None
        for inv in obj.invoices:
            if inv.ref.find("FREIGHT")!=-1:
                freight_inv=inv
        inv_vals = {
            "type": "out",
            "inv_type": "invoice",
            "contact_id": obj.contact_id.id,
            "lines": [],
            "company_id": obj.company_id.id,
            "ref": "CUSTOMER %s"%obj.number,
            "related_id": "sale.order,%s"%obj.id,
            "company_id": obj.company_id.id,
            "currency_id": obj.currency_id.id,
        }
        if freight_inv:
            inv_vals["number"]=freight_inv.number
        for line in obj.lines:
            prod=line.product_id
            qty_received=line.qty_produced or 0
            line_vals = {
                "product_id": prod.id,
                "description": prod.description or "/",
                "qty": qty_received,
                "uom_id": line.uom_id.id,
                "unit_price": line.unit_price,
                "account_id": prod.sale_account_id.id,
                "tax_id": prod.sale_tax_id.id,
                "related_id": "sale.order,%s"%obj.id,
                "discount": line.discount,
                "discount_amount": line.discount_amount,
            }
            line_vals["amount"]=line_vals["qty"]*line_vals["unit_price"]
            inv_vals["lines"].append(("create",line_vals))
        if not inv_vals["lines"]:
            raise Exception("Nothing to invoice")
        access.set_active_company(obj.company_id.id)
        if freight_inv:
            freight_inv.delete()
        inv_id = get_model("account.invoice").create(inv_vals, {"type": "out", "inv_type": "invoice"})
        inv=get_model("account.invoice").browse(inv_id)
        return {
            "next": {
                "name": "view_invoice",
                "active_id": inv_id,
            },
            "flash": "Invoice %s created from sales order" % inv.number,
            "invoice_id": inv_id,
        }

    def done(self,ids,context={}):
        super().done(ids,context=context)
        obj=self.browse(ids[0])
        if obj.supplier_type=="internal":
            labor_inv=False
            cust_inv=False
            for inv in obj.invoices:
                if inv.ref.find("LABOR")!=-1:
                    labor_inv=True
                if inv.ref.find("CUSTOMER")!=-1:
                    cust_inv=True
            if not labor_inv:
                raise Exception("Missing labor invoice")
            if not cust_inv:
                raise Exception("Missing customer invoice")

    def delete_related(self,ids,context={}):
        user_id=access.get_active_user()
        access.set_active_user(1)
        try:
            obj=self.browse(ids[0])
            for inv in obj.invoices:
                if inv.state=="paid":
                    raise Exception("Invoice %s is already paid"%inv.number)
                inv.to_draft()
                inv.delete()
            for pick in obj.pickings:
                pick.to_draft()
                pick.delete()
            for mfg in obj.production_orders:
                mfg.to_draft()
                mfg.delete()
            for purch in obj.purchase_orders:
                purch.to_draft()
                purch.delete()
            for sale in obj.sale_orders:
                sale.delete_related()
                sale.to_draft()
                sale.delete()
        finally:
            access.set_active_user(user_id)

Order.register()
