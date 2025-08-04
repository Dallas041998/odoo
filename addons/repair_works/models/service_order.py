from odoo import models, fields

class ServiceOrder(models.Model):
    _name = 'repair.service_order'
    _description = 'Service Order'

    equipment_id = fields.Many2one('repair.equipment', string='Equipment')
    description = fields.Text(string='Description')
    status = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Done')
    ], string='Status', default='draft')