from odoo import models, fields, api

class PosFoodMenu(models.Model):
    _name = 'pos.food.menu'
    _description = 'Menu Item'
    
    name = fields.Char(string='Menu Name', required=True)
    category = fields.Selection([
        ('appetizer', 'อาหารว่าง'),
        ('main_course', 'อาหารจานหลัก'),
        ('dessert', 'ขนมหวาน'),
        ('beverage', 'เครื่องดื่ม'),
    ], string='Category')
    price = fields.Float(string='Price', required=True)
    image = fields.Image(string='Image', max_width=1024, max_height=1024)
    is_available = fields.Boolean(string='Available', default=True)
    recipe_line_ids = fields.One2many('pos.food.recipe.line', 'menu_id', string='Recipe')