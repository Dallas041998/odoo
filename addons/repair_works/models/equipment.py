from odoo import models, fields

class Equipment(models.Model)
    _name = 'repair.equipment'  
    _description = 'Equipment'

    name = fields.Char(string='Name', required=True)
    serial_number = fields.Char(string='Serial Number')
    location = fields.Char(string='Location')