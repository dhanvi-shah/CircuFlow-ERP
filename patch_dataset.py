"""Patch web DataSet readonly callback.

Odoo's ``_call_kw_readonly`` uses ``request.registry[model]``. After
``Registry.check_signaling`` / ``Registry.new``, the cursor's transaction can
still be tied to a registry instance that does not match ``request.registry``,
or the merged routing may still reference the stock callback. We resolve the
registry the same way as :class:`~odoo.orm.environments.Environment` (prefer
``request.env.registry`` when ``request.env`` exists, else ``Registry(dbname)``).
"""

import logging

from werkzeug.exceptions import NotFound

from odoo.http import request
from odoo.modules.registry import Registry

_logger = logging.getLogger(__name__)


def _registry_for_readonly_rpc():
    """Registry that matches ``request.env[model]`` used by ``call_kw``."""
    env = getattr(request, "env", None)
    if env is not None and getattr(env, "registry", None) is not None:
        return env.registry
    dbname = getattr(request, "db", None)
    if dbname:
        return Registry(dbname)
    return request.registry


def _recycle_call_kw_readonly(controller_self, rule, args):
    """Same logic as web DataSet._call_kw_readonly with a stable registry lookup."""
    params = request.get_json_data()["params"]
    model_name = params["model"]
    reg = _registry_for_readonly_rpc()
    try:
        model_class = reg[model_name]
    except KeyError as e:
        raise NotFound() from e
    method_name = params["method"]
    for cls in model_class.mro():
        method = getattr(cls, method_name, None)
        if method is not None and hasattr(method, "_readonly"):
            return method._readonly
    return False


def apply_dataset_readonly_patch():
    try:
        from odoo.addons.web.controllers import dataset
    except ImportError:
        _logger.warning("recycle_management: web.controllers.dataset not importable, readonly patch skipped")
        return False

    ds = dataset.DataSet
    patched_any = False
    for attr in ("call_kw", "call_button"):
        fn = getattr(ds, attr, None)
        if fn is None or not hasattr(fn, "original_routing"):
            continue
        fn.original_routing["readonly"] = _recycle_call_kw_readonly
        patched_any = True

    if not patched_any:
        _logger.warning(
            "recycle_management: DataSet call_kw/call_button missing original_routing; readonly patch skipped"
        )
        return False

    try:
        for reg in list(Registry.registries.values()):
            try:
                reg.clear_cache("routing")
            except Exception as exc:  # noqa: BLE001
                _logger.debug("recycle_management: routing cache clear failed: %s", exc)
    except Exception as exc:  # noqa: BLE001
        _logger.debug("recycle_management: routing cache clear skipped: %s", exc)

    return True
