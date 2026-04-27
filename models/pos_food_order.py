from odoo import models, fields, api

class PosFoodOrder(models.Model):
    _name = 'pos.food.order'
    _description = 'Restaurant Order'

    name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, default='New')
    table_id = fields.Many2one('pos.food.table', string='Table', required=True)
    waiter_id = fields.Many2one('res.users', string='Waiter (พนักงาน)', default=lambda self: self.env.user)
    state = fields.Selection([
        ('draft', 'Draft (รับออเดอร์)'),
        ('cooking', 'Cooking (กำลังทำ)'),
        ('served', 'Served (เสิร์ฟแล้ว)'),
        ('paid', 'Paid (จ่ายเงินแล้ว)')
    ], string='Status', default='draft')
    
    line_ids = fields.One2many('pos.food.order.line', 'order_id', string='Order Lines')
    total_amount = fields.Float(string='Total Amount', compute='_compute_total_amount', store=True)

    @api.depends('line_ids.subtotal')
    def _compute_total_amount(self):
        for order in self:
            order.total_amount = sum(line.subtotal for line in order.line_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = 'ORD/' + str(fields.Datetime.now().strftime("%Y%m%d/%H%M%S"))
        return super().create(vals_list)

    def write(self, vals):
        # ตรวจสอบว่ามีการเปลี่ยนสถานะเป็น paid (จ่ายเงินแล้ว)
        if vals.get('state') == 'paid':
            for order in self:
                # ทำการตัดสต๊อกก็ต่อเมื่อสถานะเดิมยังไม่ใช่ paid (ป้องกันตัดซ้ำ)
                if order.state != 'paid':
                    for line in order.line_ids:
                        menu = line.menu_id
                        quantity_ordered = line.quantity
                        # วนลูปดูสูตรอาหารของเมนูนี้
                        for recipe in menu.recipe_line_ids:
                            ingredient = recipe.ingredient_id
                            # คำนวณจำนวนวัตถุดิบที่ใช้ทั้งหมด
                            total_used = recipe.quantity_required * quantity_ordered
                            # ตัดสต๊อก
                            ingredient.stock_quantity -= total_used
                            
        return super().write(vals)

class PosFoodOrderLine(models.Model):
    _name = 'pos.food.order.line'
    _description = 'Order Line'

    order_id = fields.Many2one('pos.food.order', string='Order Reference', ondelete='cascade')
    menu_id = fields.Many2one('pos.food.menu', string='Menu Item', required=True)
    menu_image = fields.Image(string='Image', related='menu_id.image', max_width=128, max_height=128)
    quantity = fields.Integer(string='Quantity', default=1, required=True)
    price_unit = fields.Float(string='Unit Price', related='menu_id.price', store=True)
    state = fields.Selection([
        ('draft', 'รอทำ'),
        ('cooking', 'กำลังทำ'),
        ('served', 'เสิร์ฟแล้ว')
    ], string='Status', default='draft')
    subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)

    def action_done(self):
        for line in self:
            line.state = 'served'
        return True

    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.price_unit
