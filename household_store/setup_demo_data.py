"""
Script to add images and additional demo data to the household store module via XML-RPC.
"""
import xmlrpc.client
import base64
import os
import sys

# Odoo connection settings
URL = 'http://localhost:8069'
DB = 'test1'
USERNAME = 'admin'
PASSWORD = 'admin'

# Image directory
IMG_DIR = r'C:\Users\autod\.gemini\antigravity\brain\7e0bfa80-0644-42b4-8aa1-df9cc54dcf70'

def get_image_base64(filename):
    """Read image file and return base64 encoded string."""
    # Find the actual file (may have timestamp suffix)
    for f in os.listdir(IMG_DIR):
        if f.startswith(filename) and f.endswith('.png'):
            filepath = os.path.join(IMG_DIR, f)
            with open(filepath, 'rb') as img:
                return base64.b64encode(img.read()).decode('utf-8')
    return False

def main():
    # Connect to Odoo
    common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
    uid = common.authenticate(DB, USERNAME, PASSWORD, {})
    if not uid:
        print("Authentication failed!")
        sys.exit(1)
    print(f"Authenticated as UID: {uid}")

    models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')

    def execute(model, method, *args, **kwargs):
        return models.execute_kw(DB, uid, PASSWORD, model, method, args, kwargs)

    # ============================================================
    # 1. Update existing products with images
    # ============================================================
    print("\n--- Updating product images ---")

    # น้ำยาล้างจาน
    product_ids = execute('store.product', 'search', [('product_code', '=', 'P001')])
    if product_ids:
        img = get_image_base64('product_dishwash')
        if img:
            execute('store.product', 'write', product_ids, {'image': img})
            print("✓ Updated image for น้ำยาล้างจาน (P001)")

    # ไม้กวาด
    product_ids = execute('store.product', 'search', [('product_code', '=', 'P002')])
    if product_ids:
        img = get_image_base64('product_broom')
        if img:
            execute('store.product', 'write', product_ids, {'image': img})
            print("✓ Updated image for ไม้กวาด (P002)")

    # ผ้าขนหนู
    product_ids = execute('store.product', 'search', [('product_code', '=', 'P003')])
    if product_ids:
        img = get_image_base64('product_towel')
        if img:
            execute('store.product', 'write', product_ids, {'image': img})
            print("✓ Updated image for ผ้าขนหนู (P003)")

    # ============================================================
    # 2. Update existing customers with images
    # ============================================================
    print("\n--- Updating customer images ---")

    cust_ids = execute('store.customer', 'search', [('name', 'like', 'วิภา')])
    if cust_ids:
        img = get_image_base64('customer_vipa')
        if img:
            execute('store.customer', 'write', cust_ids, {
                'image': img,
                'address': '123/45 ถ.สุขุมวิท แขวงคลองเตย เขตคลองเตย กรุงเทพฯ 10110',
            })
            print("✓ Updated image & address for คุณวิภา สุขสันต์")

    cust_ids = execute('store.customer', 'search', [('name', 'like', 'ประเสริฐ')])
    if cust_ids:
        img = get_image_base64('customer_prasert')
        if img:
            execute('store.customer', 'write', cust_ids, {
                'image': img,
                'address': '789/10 ถ.พหลโยธิน แขวงลาดยาว เขตจตุจักร กรุงเทพฯ 10900',
            })
            print("✓ Updated image & address for คุณประเสริฐ มั่งมี")

    # ============================================================
    # 3. Add more products with images
    # ============================================================
    print("\n--- Adding new products ---")

    new_products = [
        {
            'name': 'ไม้ถูพื้น',
            'product_code': 'P004',
            'category_id': execute('store.product.category', 'search', [('name', '=', 'อุปกรณ์ทำความสะอาด')])[0],
            'cost_price': 250,
            'sale_price': 450,
            'quantity_on_hand': 20,
            'minimum_stock': 3,
            'unit': 'piece',
            'description': 'ไม้ถูพื้นระบบสปิน พร้อมถังปั่น ด้ามสแตนเลส หัวไมโครไฟเบอร์',
            'image': get_image_base64('product_mop'),
        },
        {
            'name': 'น้ำยาซักผ้า',
            'product_code': 'P005',
            'category_id': execute('store.product.category', 'search', [('name', '=', 'อุปกรณ์ทำความสะอาด')])[0],
            'cost_price': 95,
            'sale_price': 159,
            'quantity_on_hand': 80,
            'minimum_stock': 10,
            'unit': 'piece',
            'description': 'น้ำยาซักผ้าสูตรเข้มข้น ขนาด 1 ลิตร หอมสดชื่น',
            'image': get_image_base64('product_detergent'),
        },
    ]

    for prod in new_products:
        existing = execute('store.product', 'search', [('product_code', '=', prod['product_code'])])
        if not existing:
            pid = execute('store.product', 'create', [prod])
            print(f"✓ Created product: {prod['name']} (ID: {pid})")
        else:
            execute('store.product', 'write', existing, prod)
            print(f"✓ Updated product: {prod['name']}")

    # ============================================================
    # 4. Add more customers
    # ============================================================
    print("\n--- Adding new customers ---")

    new_customers = [
        {
            'name': 'คุณสมศรี มีทรัพย์',
            'phone': '084-555-6677',
            'email': 'somsri@email.com',
            'customer_type': 'regular',
            'address': '55/8 หมู่ 3 ต.ในเมือง อ.เมือง จ.ขอนแก่น 40000',
        },
        {
            'name': 'คุณธนพล เจริญกิจ',
            'phone': '091-888-9900',
            'email': 'thanapol@email.com',
            'customer_type': 'member',
            'address': '222/1 ถ.นิมมานเหมินท์ ต.สุเทพ อ.เมือง จ.เชียงใหม่ 50200',
        },
    ]

    for cust in new_customers:
        existing = execute('store.customer', 'search', [('email', '=', cust['email'])])
        if not existing:
            cid = execute('store.customer', 'create', [cust])
            print(f"✓ Created customer: {cust['name']} (ID: {cid})")
        else:
            print(f"  Already exists: {cust['name']}")

    # ============================================================
    # 5. Update employee data
    # ============================================================
    print("\n--- Updating employee data ---")

    emp_ids = execute('store.employee', 'search', [('employee_code', '=', 'EMP001')])
    if emp_ids:
        execute('store.employee', 'write', emp_ids, {
            'email': 'somchai@store.com',
            'address': '99/5 หมู่ 2 ต.บางพลี อ.บางพลี จ.สมุทรปราการ 10540',
        })
        print("✓ Updated สมชาย ใจดี")

    emp_ids = execute('store.employee', 'search', [('employee_code', '=', 'EMP002')])
    if emp_ids:
        execute('store.employee', 'write', emp_ids, {
            'email': 'suda@store.com',
            'address': '47/12 ซ.อ่อนนุช 44 แขวงสวนหลวง เขตสวนหลวง กรุงเทพฯ 10250',
        })
        print("✓ Updated สุดา แสนสวย")

    # Add more employees
    new_employees = [
        {
            'name': 'วิรัช ขยันทำ',
            'employee_code': 'EMP003',
            'phone': '063-222-3344',
            'email': 'wirat@store.com',
            'position': 'stock_keeper',
            'department': 'warehouse',
            'salary': 16000,
            'address': '88/3 ถ.เพชรเกษม แขวงบางแค เขตบางแค กรุงเทพฯ 10160',
        },
        {
            'name': 'กมลชนก รักงาน',
            'employee_code': 'EMP004',
            'phone': '097-444-5566',
            'email': 'kamonchanok@store.com',
            'position': 'sales',
            'department': 'sales',
            'salary': 17000,
            'address': '156 ถ.รัชดาภิเษก แขวงดินแดง เขตดินแดง กรุงเทพฯ 10400',
        },
    ]

    for emp in new_employees:
        existing = execute('store.employee', 'search', [('employee_code', '=', emp['employee_code'])])
        if not existing:
            eid = execute('store.employee', 'create', [emp])
            print(f"✓ Created employee: {emp['name']} (ID: {eid})")
        else:
            print(f"  Already exists: {emp['name']}")

    print("\n=== All done! ===")
    print("Summary:")
    print(f"  Products: {execute('store.product', 'search_count', [])}")
    print(f"  Customers: {execute('store.customer', 'search_count', [])}")
    print(f"  Employees: {execute('store.employee', 'search_count', [])}")
    print(f"  Sale Orders: {execute('store.sale', 'search_count', [])}")

if __name__ == '__main__':
    main()
