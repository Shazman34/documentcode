from netforce.model import Model, fields, get_model
from netforce import access
from datetime import *


class Items(Model):
    _name = "lazada.order.item"
    _fields = {
        "order_id": fields.Many2One("lazada.order","Lazada Order"),
        "item_id": fields.Char("Item ID"),
        "item_name": fields.Text("Item Name"),
        "item_sku": fields.Char("Item SKU"),
        "model_id": fields.Char("Model ID"),
        "model_name": fields.Char("Model Name"),
        "model_quantity_purchased": fields.Integer("Model Quantity Purchased"),
        "model_original_price": fields.Decimal("Model Original Price"),
        "model_discounted_price": fields.Decimal("Model Discounted Price"),
        "warehouse_code": fields.Char("Warehouse Code"),
        "weight": fields.Decimal("Weight"),
        "order_flag": fields.Char("Order Flag"),
        "tax_amount": fields.Char("Tax Amount"),
        "variation": fields.Char("Variation"),
        "product_id": fields.Char("Product id"),
        "shop_id": fields.Char("Shope"),
        "invoice_number": fields.Char("Invoice Number"),
        "product_detail_url": fields.Text("Product Detail Url"),
        "shipping_type": fields.Char("Shipping Type"),
        "shipping_provider_type": fields.Char("Shipping Provider Type"),
        "item_price": fields.Char("Item Price"),
        "shipping_service_cost": fields.Char("Shipping Service Cost"),
        "tracking_code": fields.Char("Tracking Code"),
        "shipping_amount": fields.Char("Shipping Amount"),
        "shipment_provider": fields.Char("Shipment Provider"),
        "voucher_amount": fields.Char("Voucher Amount"),
        "digital_delivery_info": fields.Char("Digital Delivery Info"),
        "extra_attributes": fields.Char("Extra Attributes")

    }

Items.register()
