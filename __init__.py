from .patch_dataset import apply_dataset_readonly_patch

apply_dataset_readonly_patch()

from . import models


def post_init_hook(env):
    """Runs on module install: re-apply patch and invalidate cached routing maps."""
    apply_dataset_readonly_patch()
    env.registry.clear_cache("routing")
    env.registry.clear_cache("templates")
    # Remove obsolete menu parents (pre-1.4); children were reassigned in XML.
    for xmlid in (
        "recycle_management.menu_production_sub",
        "recycle_management.menu_recycling_sub",
    ):
        menu = env.ref(xmlid, raise_if_not_found=False)
        if menu:
            menu.unlink()
