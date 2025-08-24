from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    # Equipment related fields
    equipment_ids = fields.One2many(
        'customer.equipment', 
        'customer_id', 
        string='Equipment',
        help='Equipment owned by this customer'
    )
    equipment_count = fields.Integer(
        string='Equipment Count',
        compute='_compute_equipment_count',
        store=True
    )
    service_order_ids = fields.One2many(
        'service.order',
        'customer_id',
        string='Service Orders'
    )
    service_order_count = fields.Integer(
        string='Service Order Count',
        compute='_compute_service_order_count',
        store=True
    )
    
    @api.depends('equipment_ids')
    def _compute_equipment_count(self):
        for partner in self:
            partner.equipment_count = len(partner.equipment_ids)
    
    @api.depends('service_order_ids')
    def _compute_service_order_count(self):
        for partner in self:
            partner.service_order_count = len(partner.service_order_ids)
    
    def action_view_equipment(self):
        """Action to view customer equipment"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Customer Equipment',
            'view_mode': 'tree,form',
            'res_model': 'customer.equipment',
            'domain': [('customer_id', '=', self.id)],
            'context': {'default_customer_id': self.id}
        }
    
    def action_view_service_orders(self):
        """Action to view service orders"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Service Orders',
            'view_mode': 'tree,form',
            'res_model': 'service.order',
            'domain': [('customer_id', '=', self.id)],
            'context': {'default_customer_id': self.id}
        }