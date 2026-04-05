from odoo import models


class IrUiView(models.Model):
    _inherit = "ir.ui.view"

    def _get_view_fields(self, view_type, models):
        """Ensure recycle.dashboard form views load every field into get_views().

        Stale ``_get_view_cache`` (templates) can yield an arch that references
        fields not listed in the collected ``models`` set, which breaks the web
        client (Field.parseFieldNode: field is undefined).
        """
        models = super()._get_view_fields(view_type, models)
        if view_type == "form" and "recycle.dashboard" in models:
            dash = self.env["recycle.dashboard"]
            models["recycle.dashboard"].update(dash._fields)
        return models
