# Part of Odoo. See LICENSE file for full copyright and licensing details.
"""Fix DB rows that still reference the old model name ``seller.product``.

The model is ``recycle.seller.product``. Stale window actions, views, and field
metadata pointing at ``seller.product`` cause AccessError or broken menus.
"""

import logging

_logger = logging.getLogger(__name__)

OLD = "seller.product"
NEW = "recycle.seller.product"


def migrate(cr, version):
    # Window actions (app / menu destinations)
    cr.execute(
        "UPDATE ir_act_window SET res_model = %s WHERE res_model = %s",
        (NEW, OLD),
    )
    if cr.rowcount:
        _logger.info(
            "recycle_management: updated %s ir.act_window rows from %s to %s",
            cr.rowcount,
            OLD,
            NEW,
        )

    # Views
    cr.execute(
        "UPDATE ir_ui_view SET model = %s WHERE model = %s",
        (NEW, OLD),
    )
    if cr.rowcount:
        _logger.info(
            "recycle_management: updated %s ir.ui.view rows from %s to %s",
            cr.rowcount,
            OLD,
            NEW,
        )

    # Many2one / Many2many field metadata (e.g. buyer.request -> seller product)
    cr.execute(
        "UPDATE ir_model_fields SET relation = %s WHERE relation = %s",
        (NEW, OLD),
    )
    if cr.rowcount:
        _logger.info(
            "recycle_management: updated %s ir.model.fields relation from %s to %s",
            cr.rowcount,
            OLD,
            NEW,
        )

    # Report actions
    cr.execute(
        "UPDATE ir_act_report_xml SET model = %s WHERE model = %s",
        (NEW, OLD),
    )
    if cr.rowcount:
        _logger.info(
            "recycle_management: updated %s ir.actions.report rows from %s to %s",
            cr.rowcount,
            OLD,
            NEW,
        )

    # Embedded actions (parent model string)
    cr.execute(
        """
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_name = 'ir_embedded_actions'
        )
        """
    )
    if cr.fetchone()[0]:
        cr.execute(
            "UPDATE ir_embedded_actions SET parent_res_model = %s WHERE parent_res_model = %s",
            (NEW, OLD),
        )
        if cr.rowcount:
            _logger.info(
                "recycle_management: updated %s ir.embedded.actions parent_res_model from %s to %s",
                cr.rowcount,
                OLD,
                NEW,
            )

    # Repoint FKs from old ir.model row to new one (when both exist)
    cr.execute(
        """
        SELECT im_old.id, im_new.id
          FROM ir_model im_old
          JOIN ir_model im_new ON im_new.model = %s
         WHERE im_old.model = %s
         LIMIT 1
        """,
        (NEW, OLD),
    )
    row = cr.fetchone()
    if not row:
        return

    old_id, new_id = row

    cr.execute(
        "UPDATE ir_act_server SET model_id = %s WHERE model_id = %s",
        (new_id, old_id),
    )
    if cr.rowcount:
        _logger.info(
            "recycle_management: repointed %s ir.act_server rows from ir.model %s to %s",
            cr.rowcount,
            old_id,
            new_id,
        )

    cr.execute(
        "UPDATE ir_rule SET model_id = %s WHERE model_id = %s",
        (new_id, old_id),
    )
    if cr.rowcount:
        _logger.info(
            "recycle_management: repointed %s ir.rule rows from ir.model %s to %s",
            cr.rowcount,
            old_id,
            new_id,
        )

    # Remove ACL rows on the old model when the same group already has access on the new model
    cr.execute(
        """
        DELETE FROM ir_model_access AS a
         WHERE a.model_id = %s
           AND EXISTS (
               SELECT 1
                 FROM ir_model_access o
                WHERE o.model_id = %s
                  AND COALESCE(o.group_id, -1) = COALESCE(a.group_id, -1)
           )
        """,
        (old_id, new_id),
    )
    if cr.rowcount:
        _logger.info(
            "recycle_management: removed %s ir.model.access rows superseded after merge",
            cr.rowcount,
        )

    cr.execute(
        "UPDATE ir_model_access SET model_id = %s WHERE model_id = %s",
        (new_id, old_id),
    )
    if cr.rowcount:
        _logger.info(
            "recycle_management: repointed %s ir.model.access rows to ir.model id %s",
            cr.rowcount,
            new_id,
        )
