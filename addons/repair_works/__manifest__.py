{
    'name': 'Repair Works',
    'version': '1.0.0',
    'category': 'Services',
    'summary': 'Manage shop services, jobs, and customer equipment',
    'description': """
        Shop & Job Management System
        =============================
        This module provides:
        - Customer equipment tracking
        - Service order management
        - Integration with existing Odoo modules
        - Equipment history and maintenance tracking
    """,
    'author': 'Mountainside Tech',
    'website': 'https://yourcompany.com',
    'depends': [
        'base',
        'sale',
        'purchase',
        'account',
        'stock',
        'product',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'views/customer_equipment_views.xml',
        'views/res_partner_views.xml',
        'views/service_order_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}