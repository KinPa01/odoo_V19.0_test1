from odoo import models, fields

class PosFoodIngredient(models.Model):
    _name = 'pos.food.ingredient'
    _description = 'Food Ingredient'

    name = fields.Char(string='Ingredient Name (ชื่อวัตถุดิบ)', required=True)
    unit = fields.Selection([
        ('g', 'Grams (กรัม)'),
        ('kg', 'Kilograms (กิโลกรัม)'),
        ('ml', 'Milliliters (มิลลิลิตร)'),
        ('piece', 'Pieces (ชิ้น/ตัว)')
    ], string='Unit (หน่วย)', required=True, default='g')
    stock_quantity = fields.Float(string='Stock Quantity (จำนวนคงเหลือ)', default=0.0)

class PosFoodRecipeLine(models.Model):
    _name = 'pos.food.recipe.line'
    _description = 'Recipe Line'

    menu_id = fields.Many2one('pos.food.menu', string='Menu Item', ondelete='cascade')
    ingredient_id = fields.Many2one('pos.food.ingredient', string='Ingredient', required=True)
    quantity_required = fields.Float(string='Quantity Required (จำนวนที่ใช้ต่อ 1 จาน)', required=True, default=1.0)
