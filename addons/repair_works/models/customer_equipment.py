from odoo import models, fields, api
from datetime import datetime

class CustomerEquipment(models.Model):
    _name = 'customer.equipment'
    _description = 'Customer Equipment'
    _rec_name = 'display_name'
    _order = 'create_date desc'
    
    # Basic Information
    name = fields.Char(string='Equipment Name', required=True)
    display_name = fields.Char(string='Display Name', compute='_compute_display_name', store=True)
    code = fields.Char(string='Equipment Code', readonly=True, copy=False)
    customer_id = fields.Many2one('res.partner', string='Customer', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product Reference')
    
    # Equipment Details
    serial_number = fields.Char(string='Serial Number')
    model = fields.Char(string='Model')
    manufacturer = fields.Char(string='Manufacturer')
    year = fields.Char(string='Year')
    
    # Equipment Type and Category
    equipment_type = fields.Selection([
        ('vehicle', 'Vehicle'),
        ('machinery', 'Machinery'),
        ('electronic', 'Electronic'),
        ('tool', 'Tool'),
        ('appliance', 'Appliance'),
        ('other', 'Other')
    ], string='Equipment Type', default='other')
    
    # Status and Condition
    state = fields.Selection([
        ('active', 'Active'),
        ('maintenance', 'Under Maintenance'),
        ('repair', 'Under Repair'),
        ('inactive', 'Inactive'),
        ('disposed', 'Disposed')
    ], string='Status', default='active', tracking=True)
    
    condition = fields.Selection([
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('broken', 'Broken')
    ], string='Condition', default='good')
    
    # Dates
    purchase_date = fields.Date(string='Purchase Date')
    warranty_end_date = fields.Date(string='Warranty End Date')
    last_service_date = fields.Date(string='Last Service Date', compute='_compute_last_service_date')
    
    # Additional Information
    notes = fields.Text(string='Notes')
    image = fields.Binary(string='Image', attachment=True)
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    
    # Service History
    service_order_ids = fields.One2many('service.order', 'equipment_id', string='Service Orders')
    service_count = fields.Integer(string='Service Count', compute='_compute_service_count')
    
    # Technical specs (can be customized based on equipment type)
    technical_specs = fields.Text(string='Technical Specifications')
    
    @api.model
    def create(self, vals):
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('customer.equipment') or 'New'
        return super(CustomerEquipment, self).create(vals)
    
    @api.depends('name', 'serial_number', 'customer_id')
    def _compute_display_name(self):
        for equipment in self:
            parts = [equipment.name]
            if equipment.serial_number:
                parts.append(f"[{equipment.serial_number}]")
            if equipment.customer_id:
                parts.append(f"- {equipment.customer_id.name}")
            equipment.display_name = ' '.join(parts)
    
    @api.depends('service_order_ids')
    def _compute_service_count(self):
        for equipment in self:
            equipment.service_count = len(equipment.service_order_ids)
    
    @api.depends('service_order_ids.date_order')
    def _compute_last_service_date(self):
        for equipment in self:
            service_orders = equipment.service_order_ids.filtered(lambda s: s.state == 'done')
            if service_orders:
                equipment.last_service_date = max(service_orders.mapped('date_order'))
            else:
                equipment.last_service_date = False
    
    def action_view_service_orders(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Service Orders',
            'view_mode': 'tree,form',
            'res_model': 'service.order',
            'domain': [('equipment_id', '=', self.id)],
            'context': {'default_equipment_id': self.id, 'default_customer_id': self.customer_id.id}
        }