from odoo import api, fields, models


class RecycleDashboard(models.TransientModel):
    _name = "recycle.dashboard"
    _description = "Recycle Management Dashboard"

    pickup_total = fields.Integer(string="Pickup Requests")
    pickup_pending = fields.Integer(string="Pickups — Pending")
    agency_total = fields.Integer(string="Agency Requests")
    agency_requested = fields.Integer(string="Agencies — Requested")
    warehouse_total = fields.Integer(string="Warehouse Lines")
    warehouse_stock_qty = fields.Float(string="Total Stock (all types)", digits=(16, 2))
    seller_product_total = fields.Integer(string="Seller Products")
    seller_product_eco_total = fields.Integer(string="Eco-friendly Products")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        Pickup = self.env["pickup.request"]
        Agency = self.env["agency.request"]
        Stock = self.env["warehouse.stock"]
        SellerProduct = self.env["recycle.seller.product"]
        res["pickup_total"] = Pickup.search_count([])
        res["pickup_pending"] = Pickup.search_count([("status", "=", "pending")])
        res["agency_total"] = Agency.search_count([])
        res["agency_requested"] = Agency.search_count([("status", "=", "requested")])
        res["warehouse_total"] = Stock.search_count([])
        lines = Stock.search([])
        res["warehouse_stock_qty"] = sum(lines.mapped("quantity_available"))
        if "seller_product_total" in self._fields:
            res["seller_product_total"] = SellerProduct.search_count([])
        if "seller_product_eco_total" in self._fields:
            res["seller_product_eco_total"] = SellerProduct.search_count([("eco_friendly", "=", True)])
        return res
