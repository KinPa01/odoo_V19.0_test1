# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class StoreEmployee(models.Model):
    _name = 'store.employee'
    _description = 'พนักงาน'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name asc'

    name = fields.Char(string='ชื่อ-นามสกุล', required=True, tracking=True)
    employee_code = fields.Char(string='รหัสพนักงาน', required=True, copy=False, tracking=True, default='New')
    phone = fields.Char(string='เบอร์โทรศัพท์', tracking=True)
    email = fields.Char(string='อีเมล', tracking=True)
    address = fields.Text(string='ที่อยู่')
    position = fields.Selection([
        ('manager', 'ผู้จัดการ'),
        ('cashier', 'แคชเชียร์'),
        ('stock_keeper', 'พนักงานคลังสินค้า'),
        ('sales', 'พนักงานขาย'),
        ('delivery', 'พนักงานจัดส่ง'),
    ], string='ตำแหน่ง', required=True, tracking=True)
    department = fields.Selection([
        ('sales', 'ฝ่ายขาย'),
        ('warehouse', 'ฝ่ายคลังสินค้า'),
        ('admin', 'ฝ่ายบริหาร'),
        ('delivery', 'ฝ่ายจัดส่ง'),
    ], string='แผนก', tracking=True)
    hire_date = fields.Date(string='วันที่เริ่มงาน', default=fields.Date.today, tracking=True)
    salary = fields.Float(string='เงินเดือน', tracking=True)
    active = fields.Boolean(string='ใช้งาน', default=True)
    image = fields.Binary(string='รูปภาพ', attachment=True)
    notes = fields.Text(string='หมายเหตุ')

    sale_ids = fields.One2many('store.sale', 'employee_id', string='รายการขาย')
    sale_count = fields.Integer(string='จำนวนการขาย', compute='_compute_sale_count')
    total_sales = fields.Float(string='ยอดขายรวม', compute='_compute_total_sales')

    _sql_constraints = [
        ('employee_code_unique', 'unique(employee_code)', 'รหัสพนักงานต้องไม่ซ้ำกัน!'),
    ]

    @api.depends('sale_ids')
    def _compute_sale_count(self):
        for record in self:
            record.sale_count = len(record.sale_ids.filtered(lambda s: s.state == 'confirmed'))

    @api.depends('sale_ids', 'sale_ids.total_amount', 'sale_ids.state')
    def _compute_total_sales(self):
        for record in self:
            record.total_sales = sum(
                record.sale_ids.filtered(lambda s: s.state == 'confirmed').mapped('total_amount')
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('employee_code') or vals.get('employee_code') == 'New':
                vals['employee_code'] = self.env['ir.sequence'].next_by_code('store.employee') or 'New'
        return super().create(vals_list)
