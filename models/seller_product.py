from odoo import fields, models


class SellerProduct(models.Model):
    _name = "recycle.seller.product"
    _description = "Seller Product"
    _order = "product_name, id"
    _rec_name = "product_name"

    seller_name = fields.Char(required=True)
    product_name = fields.Char(required=True)
    price = fields.Float(required=True, digits=(16, 2))
    quantity_available = fields.Float(required=True, digits=(16, 2), default=0.0)
    eco_friendly = fields.Boolean(default=False)
    category_ids = fields.Many2many(
        "recycle.product.category",
        "seller_product_category_rel",
        "seller_product_id",
        "category_id",
        string="Categories",
    )
    description = fields.Text()
