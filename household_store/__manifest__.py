# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'ระบบจัดการร้านค้าของใช้',
    'version': '19.0.1.0.0',
    'category': 'Sales',
    'summary': 'ระบบจัดการลูกค้า พนักงาน สินค้า และการขาย สำหรับร้านค้าของใช้',
    'description': """
ระบบจัดการร้านค้าของใช้ (Household Store Management)
=====================================================

โมดูลนี้ประกอบด้วย:
- จัดการข้อมูลลูกค้า (Customers)
- จัดการข้อมูลพนักงาน (Employees)
- จัดการรายการสินค้า (Products) พร้อมหมวดหมู่
- บันทึกการขาย (Sales Orders)
- แดชบอร์ดภาพรวมร้านค้า
    """,
    'author': 'Custom',
    'website': '',
    'depends': ['base', 'mail', 'product', 'sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'data/store_sequence.xml',
        'views/store_customer_views.xml',
        'views/store_employee_views.xml',
        'views/store_product_views.xml',
        'views/store_sale_views.xml',
        'views/store_dashboard_views.xml',
        'views/store_menus.xml',
        'data/store_data.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'sequence': 1,
    'images': [],
}
