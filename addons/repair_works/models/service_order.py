from odoo import models, fields, api
from datetime import datetime, timedelta

class ServiceOrder(models.Model):
    _name = 'service.order'
    _description = 'Service Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_order desc'
    
    # Basic Information
    name = fields.Char(string='Service Order', required=True, copy=False, readonly=True, default='New')
    customer_id = fields.Many2one('res.partner', string='Customer', required=True, tracking=True)
    equipment_id = fields.Many2one('customer.equipment', string='Equipment', 
                                  domain="[('customer_id', '=', customer_id)]",
                                  tracking=True)
    
    # Equipment Information (Auto-populated from equipment_id)
    equipment_serial = fields.Char(related='equipment_id.serial_number', string='Serial Number', readonly=True)
    equipment_model = fields.Char(related='equipment_id.model', string='Model', readonly=True)
    equipment_manufacturer = fields.Char(related='equipment_id.manufacturer', string='Manufacturer', readonly=True)
    
    # Order Details
    date_order = fields.Datetime(string='Order Date', default=fields.Datetime.now, required=True, tracking=True)
    scheduled_date = fields.Datetime(string='Scheduled Date', tracking=True)
    completion_date = fields.Datetime(string='Completion Date', tracking=True)
    
    # Service Type
    service_type = fields.Selection([
        ('maintenance', 'Routine Maintenance'),
        ('repair', 'Repair'),
        ('inspection', 'Inspection'),
        ('installation', 'Installation'),
        ('emergency', 'Emergency Service'),
        ('warranty', 'Warranty Service'),
        ('other', 'Other')
    ], string='Service Type', default='maintenance', required=True, tracking=True)
    
    priority = fields.Selection([
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], string='Priority', default='normal', tracking=True)
    
    # Problem and Solution
    problem_description = fields.Text(string='Problem Description', tracking=True)
    diagnosis = fields.Text(string='Diagnosis')
    work_performed = fields.Text(string='Work Performed')
    recommendations = fields.Text(string='Recommendations')
    
    # Technician Assignment
    technician_id = fields.Many2one('res.users', string='Assigned Technician', tracking=True)
    technician_notes = fields.Text(string='Technician Notes')
    
    # Parts and Labor
    service_line_ids = fields.One2many('service.order.line', 'order_id', string='Service Lines')
    
    # Financial
    currency_id = fields.Many2one('res.currency', string='Currency', 
                                 default=lambda self: self.env.company.currency_id)
    labor_amount = fields.Monetary(string='Labor Amount', currency_field='currency_id')
    parts_amount = fields.Monetary(string='Parts Amount', currency_field='currency_id', 
                                  compute='_compute_parts_amount', store=True)
    total_amount = fields.Monetary(string='Total Amount', currency_field='currency_id',
                                  compute='_compute_total_amount', store=True)
    
    # Invoice Integration
    invoice_id = fields.Many2one('account.move', string='Invoice', readonly=True)
    invoice_state = fields.Selection(related='invoice_id.state', string='Invoice Status', readonly=True)
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('done', 'Completed'),
        ('invoiced', 'Invoiced'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    # Additional Fields
    company_id = fields.Many2one('res.company', string='Company', 
                                default=lambda self: self.env.company)
    notes = fields.Text(string='Internal Notes')
    customer_signature = fields.Binary(string='Customer Signature', attachment=True)
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('service.order') or 'New'
        return super(ServiceOrder, self).create(vals)
    
    @api.onchange('customer_id')
    def _onchange_customer_id(self):
        """Clear equipment when customer changes"""
        self.equipment_id = False
        if self.customer_id:
            return {'domain': {'equipment_id': [('customer_id', '=', self.customer_id.id)]}}
        else:
            return {'domain': {'equipment_id': []}}
    
    @api.onchange('equipment_id')
    def _onchange_equipment_id(self):
        """Auto-populate equipment details when equipment is selected"""
        if self.equipment_id:
            # You can add more auto-population logic here
            pass
    
    @api.depends('service_line_ids.subtotal')
    def _compute_parts_amount(self):
        for order in self:
            order.parts_amount = sum(order.service_line_ids.mapped('subtotal'))
    
    @api.depends('labor_amount', 'parts_amount')
    def _compute_total_amount(self):
        for order in self:
            order.total_amount = order.labor_amount + order.parts_amount
    
    def action_confirm(self):
        self.ensure_one()
        self.state = 'confirmed'
        # Update equipment status
        if self.equipment_id:
            self.equipment_id.state = 'maintenance'
    
    def action_start(self):
        self.ensure_one()
        self.state = 'in_progress'
    
    def action_complete(self):
        self.ensure_one()
        self.state = 'done'
        self.completion_date = fields.Datetime.now()
        # Update equipment status
        if self.equipment_id:
            self.equipment_id.state = 'active'
    
    def action_cancel(self):
        self.ensure_one()
        self.state = 'cancelled'
        # Reset equipment status if needed
        if self.equipment_id and self.equipment_id.state == 'maintenance':
            self.equipment_id.state = 'active'
    
    def action_create_invoice(self):
        """Create invoice from service order"""
        self.ensure_one()
        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.customer_id.id,
            'invoice_date': fields.Date.today(),
            'ref': self.name,
            'invoice_line_ids': []
        }
        
        # Add labor line
        if self.labor_amount > 0:
            invoice_vals['invoice_line_ids'].append((0, 0, {
                'name': f'Labor for Service Order {self.name}',
                'quantity': 1,
                'price_unit': self.labor_amount,
            }))
        
        # Add parts lines
        for line in self.service_line_ids:
            invoice_vals['invoice_line_ids'].append((0, 0, {
                'product_id': line.product_id.id,
                'name': line.description or line.product_id.name,
                'quantity': line.quantity,
                'price_unit': line.price_unit,
            }))
        
        invoice = self.env['account.move'].create(invoice_vals)
        self.invoice_id = invoice
        self.state = 'invoiced'
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'view_mode': 'form',
            'target': 'current',
        }


class ServiceOrderLine(models.Model):
    _name = 'service.order.line'
    _description = 'Service Order Line'
    
    order_id = fields.Many2one('service.order', string='Service Order', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    description = fields.Text(string='Description')
    quantity = fields.Float(string='Quantity', default=1.0, required=True)
    price_unit = fields.Float(string='Unit Price', required=True)
    subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)
    
    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.price_unit
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.price_unit = self.product_id.list_price
            self.description = self.product_id.name
