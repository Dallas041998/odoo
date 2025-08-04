{
    'name': 'Repair Works',
    'version': '1.0',
    'summary': 'Manage Equipment and Service Orders',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/equipment_views.xml',
        'views/service_order_views.xml',
        'views/menu.xml',
    ],
    'application': True,
}