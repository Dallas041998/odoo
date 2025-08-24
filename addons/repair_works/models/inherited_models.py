from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    is_equipment = fields.Boolean(string='Is Equipment', 
                                 help='Check if this product can be tracked as customer equipment')
    is_service_part = fields.Boolean(string='Is Service Part',
                                    help='Check if this product is used in service orders')

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    service_order_ids = fields.One2many('service.order', 'invoice_id', string='Service Orders')
    service_order_count = fields.Integer(string='Service Order Count', 
                                        compute='_compute_service_order_count')
    
    @api.depends('service_order_ids')
    def _compute_service_order_count(self):
        for invoice in self:
            invoice.service_order_count = len(invoice.service_order_ids)