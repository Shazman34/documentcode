from netforce.model import Model, fields, get_model
from netforce import access
from datetime import *


class Items(Model):
    _name = "shopee.order.item"
    _fields = {
        "order_id": fields.Many2One("shopee.order","Shopee Order"),
        "item_id": fields.Char("Item ID"),
        "item_name": fields.Char("Item Name"),
        "item_sku": fields.Char("Item SKU"),
        "model_id": fields.Char("Model ID"),
        "model_name": fields.Char("Model Name"),
        "model_quantity_purchased": fields.Integer("Model Quantity Purchased"),
        "model_original_price": fields.Decimal("Model Original Price"),
        "model_discounted_price": fields.Decimal("Model Discounted Price"),
        "wholesale": fields.Boolean("Wholesale"),
        "weight": fields.Decimal("Weight"),
        
        # For Escrow Details
        "original_price": fields.Decimal("Original Price"),
        "discounted_price": fields.Decimal("Discounted Price"),
        "discount_from_coin": fields.Decimal("Discount From Coin"),
        "discount_from_voucher_shopee": fields.Decimal("Discount From Voucher Shopee"),
        "discount_from_voucher_seller": fields.Decimal("Discount From Voucher Seller"),
        "activity_type": fields.Char("Activity Type"),
        "activity_id": fields.Integer("Activity ID"),
        "is_main_item": fields.Boolean("Main Item"),
        "quantity_purchased": fields.Integer("Quantity Purchased"),
        
    }

Items.register()
