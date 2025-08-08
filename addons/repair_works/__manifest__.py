{
    'name': 'Repair Works',
    'version': '1.0',
    'summary': 'Manage Equipment and Service Orders',
    'depends': ['base'],
    'data': [
        'security/repair_security.xml',
        'security/ir.model.access.csv',
        'views/equipment_views.xml',
        'views/service_order_views.xml',
        'views/repair_menus.xml',
    ],
    'application': True,
}