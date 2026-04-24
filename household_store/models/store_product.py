# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class StoreProductCategory(models.Model):
    _name = 'store.product.category'
    _description = 'หมวดหมู่สินค้า'
    _order = 'sequence, name'

    name = fields.Char(string='ชื่อหมวดหมู่', required=True)
    sequence = fields.Integer(string='ลำดับ', default=10)
    description = fields.Text(string='รายละเอียด')
    active = fields.Boolean(string='ใช้งาน', default=True)
    product_count = fields.Integer(string='จำนวนสินค้า', compute='_compute_product_count')
    product_ids = fields.One2many('store.product', 'category_id', string='สินค้า')

    @api.depends('product_ids')
    def _compute_product_count(self):
        for record in self:
            record.product_count = len(record.product_ids)


class StoreProduct(models.Model):
    _name = 'store.product'
    _description = 'สินค้า'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name asc'

    name = fields.Char(string='ชื่อสินค้า', required=True, tracking=True)
    product_code = fields.Char(string='รหัสสินค้า', required=True, copy=False, tracking=True, default='New')
    category_id = fields.Many2one('store.product.category', string='หมวดหมู่', required=True, tracking=True)
    description = fields.Text(string='รายละเอียดสินค้า')
    cost_price = fields.Float(string='ราคาทุน', required=True, tracking=True)
    sale_price = fields.Float(string='ราคาขาย', required=True, tracking=True)
    quantity_on_hand = fields.Float(string='จำนวนคงเหลือ', default=0, tracking=True)
    minimum_stock = fields.Float(string='จำนวนขั้นต่ำ', default=5,
                                  help='แจ้งเตือนเมื่อสินค้าเหลือน้อยกว่าจำนวนนี้')
    unit = fields.Selection([
        ('piece', 'ชิ้น'),
        ('pack', 'แพ็ค'),
        ('box', 'กล่อง'),
        ('kg', 'กิโลกรัม'),
        ('liter', 'ลิตร'),
        ('meter', 'เมตร'),
        ('set', 'ชุด'),
    ], string='หน่วย', default='piece', required=True)
    barcode = fields.Char(string='บาร์โค้ด', copy=False)
    image = fields.Binary(string='รูปสินค้า', attachment=True)
    active = fields.Boolean(string='ใช้งาน', default=True)
    notes = fields.Text(string='หมายเหตุ')

    profit_margin = fields.Float(string='กำไร (บาท)', compute='_compute_profit', store=True)
    profit_percentage = fields.Float(string='กำไร (%)', compute='_compute_profit', store=True)
    stock_status = fields.Selection([
        ('in_stock', 'มีสินค้า'),
        ('low_stock', 'สินค้าใกล้หมด'),
        ('out_of_stock', 'สินค้าหมด'),
    ], string='สถานะสต็อก', compute='_compute_stock_status', store=True)

    _sql_constraints = [
        ('product_code_unique', 'unique(product_code)', 'รหัสสินค้าต้องไม่ซ้ำกัน!'),
        ('barcode_unique', 'unique(barcode)', 'บาร์โค้ดต้องไม่ซ้ำกัน!'),
    ]

    @api.depends('cost_price', 'sale_price')
    def _compute_profit(self):
        for record in self:
            record.profit_margin = record.sale_price - record.cost_price
            if record.cost_price > 0:
                record.profit_percentage = ((record.sale_price - record.cost_price) / record.cost_price) * 100
            else:
                record.profit_percentage = 0

    @api.depends('quantity_on_hand', 'minimum_stock')
    def _compute_stock_status(self):
        for record in self:
            if record.quantity_on_hand <= 0:
                record.stock_status = 'out_of_stock'
            elif record.quantity_on_hand <= record.minimum_stock:
                record.stock_status = 'low_stock'
            else:
                record.stock_status = 'in_stock'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('product_code') or vals.get('product_code') == 'New':
                vals['product_code'] = self.env['ir.sequence'].next_by_code('store.product') or 'New'
        return super().create(vals_list)
