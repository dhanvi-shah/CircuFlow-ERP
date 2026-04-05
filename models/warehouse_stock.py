from odoo import fields, models

from .waste_constants import WASTE_TYPE_SELECTION


class WarehouseStock(models.Model):
    _name = "warehouse.stock"
    _description = "Warehouse Stock"
    _order = "warehouse_name, waste_type"

    warehouse_name = fields.Char(required=True)
    waste_type = fields.Selection(WASTE_TYPE_SELECTION, required=True)
    quantity_available = fields.Float(required=True, digits=(16, 2))

    def name_get(self):
        type_labels = dict(WASTE_TYPE_SELECTION)
        return [
            (
                rec.id,
                f"{rec.warehouse_name} ({type_labels.get(rec.waste_type, rec.waste_type)})",
            )
            for rec in self
        ]
