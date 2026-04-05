from odoo import fields, models


class RecycleProductCategory(models.Model):
    """Tag model for categories (Many2many on seller and buyer records)."""

    _name = "recycle.product.category"
    _description = "Product Category (Tag)"
    _order = "name"

    name = fields.Char(string="Name", required=True)
