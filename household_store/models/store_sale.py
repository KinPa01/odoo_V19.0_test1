# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class StoreSale(models.Model):
    _name = 'store.sale'
    _description = 'รายการขาย'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sale_date desc, id desc'

    name = fields.Char(string='เลขที่ใบขาย', required=True, copy=False, readonly=True,
                       default='New', tracking=True)
    sale_date = fields.Datetime(string='วันที่ขาย', default=fields.Datetime.now, required=True, tracking=True)
    customer_id = fields.Many2one('store.customer', string='ลูกค้า / รหัสลูกค้า', required=True, tracking=True)
    employee_id = fields.Many2one('store.employee', string='พนักงานขาย / รหัสพนักงาน', required=True, tracking=True)
    line_ids = fields.One2many('store.sale.line', 'sale_id', string='รายการสินค้า')
    state = fields.Selection([
        ('draft', 'ร่าง'),
        ('confirmed', 'ยืนยัน'),
        ('cancelled', 'ยกเลิก'),
    ], string='สถานะ', default='draft', tracking=True)
    notes = fields.Text(string='หมายเหตุ')

    total_amount = fields.Float(string='ยอดรวม', compute='_compute_total', store=True)
    total_cost = fields.Float(string='ต้นทุนรวม', compute='_compute_total', store=True)
    total_profit = fields.Float(string='กำไรรวม', compute='_compute_total', store=True)
    line_count = fields.Integer(string='จำนวนรายการ', compute='_compute_total', store=True)

    payment_method = fields.Selection([
        ('cash', 'เงินสด'),
        ('transfer', 'โอนเงิน'),
        ('credit', 'เครดิต'),
    ], string='วิธีชำระเงิน', default='cash', tracking=True)
    discount = fields.Float(string='ส่วนลด (บาท)', default=0)
    net_total = fields.Float(string='ยอดสุทธิ', compute='_compute_net_total', store=True)

    @api.depends('line_ids.subtotal', 'line_ids.cost_subtotal')
    def _compute_total(self):
        for record in self:
            record.total_amount = sum(record.line_ids.mapped('subtotal'))
            record.total_cost = sum(record.line_ids.mapped('cost_subtotal'))
            record.total_profit = record.total_amount - record.total_cost
            record.line_count = len(record.line_ids)

    @api.depends('total_amount', 'discount')
    def _compute_net_total(self):
        for record in self:
            record.net_total = record.total_amount - record.discount

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('store.sale') or 'New'
        return super().create(vals_list)

    def action_confirm(self):
        for record in self:
            if not record.line_ids:
                raise ValidationError('กรุณาเพิ่มรายการสินค้าก่อนยืนยัน!')
            for line in record.line_ids:
                if line.product_id.quantity_on_hand < line.quantity:
                    raise ValidationError(
                        f'สินค้า "{line.product_id.name}" มีไม่เพียงพอ! '
                        f'(คงเหลือ: {line.product_id.quantity_on_hand} {dict(line.product_id._fields["unit"].selection).get(line.product_id.unit, "")})'
                    )
                line.product_id.quantity_on_hand -= line.quantity
            record.state = 'confirmed'

    def action_cancel(self):
        for record in self:
            if record.state == 'confirmed':
                for line in record.line_ids:
                    line.product_id.quantity_on_hand += line.quantity
            record.state = 'cancelled'

    def action_draft(self):
        for record in self:
            record.state = 'draft'

    def action_clear_lines(self):
        for record in self:
            if record.state == 'draft':
                record.line_ids.unlink()


class StoreSaleLine(models.Model):
    _name = 'store.sale.line'
    _description = 'รายการสินค้าในใบขาย'
    _order = 'sequence, id'

    sale_id = fields.Many2one('store.sale', string='ใบขาย', required=True, ondelete='cascade')
    sequence = fields.Integer(string='ลำดับ', default=10)
    product_id = fields.Many2one('store.product', string='สินค้า', required=True)
    quantity = fields.Float(string='จำนวน', required=True, default=1)
    unit_price = fields.Float(string='ราคาต่อหน่วย', required=True)
    cost_price = fields.Float(string='ราคาทุน')
    subtotal = fields.Float(string='รวม', compute='_compute_subtotal', store=True)
    cost_subtotal = fields.Float(string='ต้นทุนรวม', compute='_compute_subtotal', store=True)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.unit_price = self.product_id.sale_price
            self.cost_price = self.product_id.cost_price

    @api.depends('quantity', 'unit_price', 'cost_price')
    def _compute_subtotal(self):
        for record in self:
            record.subtotal = record.quantity * record.unit_price
            record.cost_subtotal = record.quantity * record.cost_price
