from odoo import _, api, fields, models


class BuyerRequest(models.Model):
    _name = "buyer.request"
    _description = "Buyer Request"
    _order = "id desc"
    _rec_name = "buyer_name"

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("ordered", "Ordered"),
            ("declined", "Declined"),
        ],
        string="Status",
        default="draft",
        required=True,
        copy=False,
    )
    buyer_name = fields.Char(required=True)
    product_needed = fields.Char(required=True)
    quantity = fields.Float(required=True, digits=(16, 2))
    budget = fields.Float(digits=(16, 2))
    selected_seller_product_id = fields.Many2one(
        "recycle.seller.product",
        string="Product chosen",
        help="Set when you Purchase or Decline a row under Available seller products.",
        readonly=True,
    )
    marketplace_seller_product_ids = fields.Many2many(
        comodel_name="recycle.seller.product",
        compute="_compute_marketplace_seller_product_ids",
        string="Available seller products",
        readonly=True,
    )

    @api.depends()
    def _compute_marketplace_seller_product_ids(self):
        products = self.env["recycle.seller.product"].search([])
        for rec in self:
            rec.marketplace_seller_product_ids = products

    def action_purchase_from_product(self, product_id):
        """Called from a seller-product row (Purchase button)."""
        self.ensure_one()
        product = self.env["recycle.seller.product"].browse(product_id).exists()
        if not product:
            return self._notification(
                _("Invalid product"),
                _("That product is no longer available."),
                "warning",
            )
        return self._finalize_purchase(product)

    def _finalize_purchase(self, product):
        self.ensure_one()
        if self.state != "draft":
            return self._notification(
                _("Already processed"),
                _("This request is no longer in draft."),
                "warning",
            )
        if product.quantity_available <= 0:
            return self._notification(
                _("Out of stock"),
                _("This product is out of stock."),
                "warning",
            )
        qty = self.quantity
        if qty <= 0:
            return self._notification(
                _("Invalid quantity"),
                _("Enter a quantity greater than zero."),
                "warning",
            )
        if qty > product.quantity_available:
            return self._notification(
                _("Insufficient stock"),
                _("%(avail)s units available for “%(product)s”; you requested %(req)s.")
                % {
                    "avail": product.quantity_available,
                    "product": product.product_name,
                    "req": qty,
                },
                "warning",
            )
        seller_name = product.seller_name
        product.write({"quantity_available": product.quantity_available - qty})
        self.write(
            {
                "state": "ordered",
                "selected_seller_product_id": product.id,
            }
        )
        return self._notification(
            _("Order placed"),
            _("Ordered “%(product)s” from %(seller)s (%(qty)s units deducted from stock).")
            % {"product": product.product_name, "seller": seller_name, "qty": qty},
            "success",
        )

    def action_decline_from_product(self, product_id):
        """Called from a seller-product row (Decline button)."""
        self.ensure_one()
        product = self.env["recycle.seller.product"].browse(product_id).exists()
        if not product:
            return self._notification(
                _("Invalid product"),
                _("That product is no longer available."),
                "warning",
            )
        if self.state != "draft":
            return self._notification(
                _("Already processed"),
                _("This request is no longer in draft."),
                "warning",
            )
        self.write(
            {
                "state": "declined",
                "selected_seller_product_id": product.id,
            }
        )
        return self._notification(
            _("Declined"),
            _("Offer declined for “%(product)s” (%(seller)s).")
            % {"product": product.product_name, "seller": product.seller_name},
            "warning",
        )

    def _notification(self, title, message, notif_type):
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": title,
                "message": message,
                "type": notif_type,
                "sticky": False,
            },
        }


class SellerProductBuyerRowActions(models.Model):
    """Row buttons on buyer form → must live here so methods always merge onto recycle.seller.product."""

    _inherit = "recycle.seller.product"

    def action_buyer_purchase(self):
        self.ensure_one()
        if self.quantity_available <= 0:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Out of stock"),
                    "message": _("This product is out of stock."),
                    "type": "warning",
                    "sticky": False,
                },
            }
        buyer_id = self.env.context.get("buyer_request_id")
        if not buyer_id:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Not available"),
                    "message": _("Use Purchase on a buyer form, under Available seller products."),
                    "type": "warning",
                    "sticky": False,
                },
            }
        buyer = self.env["buyer.request"].browse(buyer_id)
        if not buyer.exists():
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Invalid request"),
                    "message": _("The buyer request could not be found."),
                    "type": "warning",
                    "sticky": False,
                },
            }
        return buyer.action_purchase_from_product(self.id)

    def action_buyer_decline(self):
        self.ensure_one()
        buyer_id = self.env.context.get("buyer_request_id")
        if not buyer_id:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Not available"),
                    "message": _("Use Decline on a buyer form, under Available seller products."),
                    "type": "warning",
                    "sticky": False,
                },
            }
        buyer = self.env["buyer.request"].browse(buyer_id)
        if not buyer.exists():
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Invalid request"),
                    "message": _("The buyer request could not be found."),
                    "type": "warning",
                    "sticky": False,
                },
            }
        return buyer.action_decline_from_product(self.id)
