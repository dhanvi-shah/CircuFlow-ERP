{
    "name": "CircuFlow ERP",
    "version": "2.0.2",
    "category": "Operations",
    "summary": "CircuFlow ERP — circular economy: recycling, warehouse, and marketplace",
    "description": """
CircuFlow ERP
=============
Recycling coordination (pickups, agency matching, warehouse stock by waste type)
and production marketplace (seller products, buyers, categories).
    """,
    "author": "Hackathon",
    "license": "LGPL-3",
    "depends": ["base", "web"],
    "post_init_hook": "post_init_hook",
    "data": [
        "security/ir_model_access.xml",
        "security/ir.model.access.csv",
        "views/recycle_actions.xml",
        "views/product_category_views.xml",
        "views/seller_product_views.xml",
        "views/buyer_request_views.xml",
        "views/pickup_request_views.xml",
        "views/agency_request_views.xml",
        "views/warehouse_stock_views.xml",
        "views/recycle_dashboard_views.xml",
        "views/recycle_menus.xml",
    ],
    "installable": True,
    "application": True,
}
