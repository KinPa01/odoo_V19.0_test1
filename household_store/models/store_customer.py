# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class StoreCustomer(models.Model):
    _name = 'store.customer'
    _description = 'ลูกค้า'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name asc'

    name = fields.Char(string='ชื่อลูกค้า', required=True, tracking=True)
    customer_code = fields.Char(string='รหัสลูกค้า', tracking=True, copy=False, default='New')
    phone = fields.Char(string='เบอร์โทรศัพท์', tracking=True)
    email = fields.Char(string='อีเมล', tracking=True)
    address = fields.Text(string='ที่อยู่')
    customer_type = fields.Selection([
        ('regular', 'ลูกค้าทั่วไป'),
        ('member', 'สมาชิก'),
        ('vip', 'VIP'),
    ], string='ประเภทลูกค้า', default='regular', tracking=True)
    member_since = fields.Date(string='เป็นสมาชิกตั้งแต่', default=fields.Date.today)
    notes = fields.Text(string='หมายเหตุ')
    active = fields.Boolean(string='ใช้งาน', default=True)
    image = fields.Binary(string='รูปภาพ', attachment=True)

    sale_ids = fields.One2many('store.sale', 'customer_id', string='รายการขาย')
    sale_count = fields.Integer(string='จำนวนการซื้อ', compute='_compute_sale_count')
    total_spent = fields.Float(string='ยอดซื้อรวม', compute='_compute_total_spent')

    @api.depends('sale_ids')
    def _compute_sale_count(self):
        for record in self:
            record.sale_count = len(record.sale_ids.filtered(lambda s: s.state == 'confirmed'))

    @api.depends('sale_ids', 'sale_ids.total_amount', 'sale_ids.state')
    def _compute_total_spent(self):
        for record in self:
            record.total_spent = sum(
                record.sale_ids.filtered(lambda s: s.state == 'confirmed').mapped('total_amount')
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('customer_code') or vals.get('customer_code') == 'New':
                vals['customer_code'] = self.env['ir.sequence'].next_by_code('store.customer') or 'New'
        return super().create(vals_list)
