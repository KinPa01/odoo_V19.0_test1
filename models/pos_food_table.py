from odoo import models, fields, api
from odoo.exceptions import ValidationError

class PosFoodTable(models.Model):
    _name = 'pos.food.table'
    _description = 'Restaurant Table'

    _sql_constraints = [
        ('name_unique', 'unique(name)', 'ชื่อโต๊ะนี้มีอยู่แล้วในระบบ กรุณาใช้ชื่ออื่น!'),
    ]

    name = fields.Char(string='Table Name / Number', required=True)
    capacity = fields.Integer(string='Capacity (Seats)', default=2)
    order_ids = fields.One2many('pos.food.order', 'table_id', string='Orders')
    state = fields.Selection([
        ('available', 'Available (ว่าง)'),
        ('occupied', 'Occupied (มีลูกค้า)'),
        ('reserved', 'Reserved (จองแล้ว)')
    ], string='Status', compute='_compute_state', store=False)

    @api.depends('order_ids.state')
    def _compute_state(self):
        for table in self:
            active_orders = table.order_ids.filtered(lambda o: o.state != 'paid')
            if active_orders:
                table.state = 'occupied'
            else:
                table.state = 'available'

    @api.constrains('name')
    def _check_unique_name(self):
        for table in self:
            if self.search_count([('name', '=', table.name)]) > 1:
                raise ValidationError('ชื่อโต๊ะ "%s" มีอยู่แล้วในระบบ กรุณาใช้ชื่ออื่น!' % table.name)
