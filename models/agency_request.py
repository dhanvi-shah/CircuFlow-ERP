from odoo import _, fields, models

from .waste_constants import WASTE_TYPE_SELECTION


class AgencyRequest(models.Model):
    _name = "agency.request"
    _description = "Agency Request"
    _order = "deadline asc, id desc"
    _rec_name = "agency_name"

    agency_name = fields.Char(required=True)
    waste_type = fields.Selection(WASTE_TYPE_SELECTION, required=True)
    quantity_required = fields.Float(required=True, digits=(16, 2))
    deadline = fields.Date(required=True)
    status = fields.Selection(
        [
            ("requested", "Requested"),
            ("matching", "Matching"),
            ("fulfilled", "Fulfilled"),
            ("cancelled", "Cancelled"),
        ],
        default="requested",
        required=True,
    )

    def action_find_match(self):
        self.ensure_one()
        self.status = "matching"
        Stock = self.env["warehouse.stock"]
        domain = [
            ("waste_type", "=", self.waste_type),
            ("quantity_available", ">=", self.quantity_required),
        ]
        match = Stock.search(domain, limit=1, order="quantity_available desc")
        if match:
            message = _("Match Found at %s") % match.warehouse_name
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Match Found"),
                    "message": message,
                    "type": "success",
                    "sticky": False,
                },
            }
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("No Match"),
                "message": _("Insufficient stock"),
                "type": "warning",
                "sticky": False,
            },
        }

    def action_fulfill(self):
        for rec in self:
            rec.status = "fulfilled"

    def action_cancel(self):
        for rec in self:
            rec.status = "cancelled"
