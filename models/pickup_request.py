from odoo import fields, models

from .waste_constants import WASTE_TYPE_SELECTION


class PickupRequest(models.Model):
    _name = "pickup.request"
    _description = "Pickup Request"
    _order = "date desc, id desc"

    name = fields.Char(string="Person Name", required=True)
    location = fields.Char(required=True)
    waste_type = fields.Selection(WASTE_TYPE_SELECTION, required=True)
    quantity = fields.Float(required=True, digits=(16, 2))
    date = fields.Date(required=True)
    status = fields.Selection(
        [
            ("pending", "Pending"),
            ("assigned", "Assigned"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="pending",
        required=True,
    )

    def action_assign(self):
        for rec in self:
            rec.status = "assigned"

    def action_complete(self):
        for rec in self:
            rec.status = "completed"

    def action_cancel(self):
        for rec in self:
            rec.status = "cancelled"
