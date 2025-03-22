from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

try:
    client = MongoClient('mongodb://localhost:27017/')
    db = client['shop_management']
    print("MongoDB connected")
except:
    print("MongoDB connection Error")

# Collections
users = db['users']
customers = db['customers']
products = db['products']
orders = db['orders']

def add_product(name=None, stock=None, category=None):
    try:
        products.insert_one({
            'name': name,
            'stock': stock,
            'category': category,
            'created_at': datetime.now()
        })
        print('Product added to db')
    except Exception as e:
        print('db_error @add_product:', str(e))

def find_user(username=None, password=None):
    try:
        user = users.find_one({
            'username': username,
            'password': password
        })
        if user:
            return {
                'id': str(user['_id']),
                'username': user['username'],
                'role': user.get('role', 'customer')
            }
        return None
    except Exception as e:
        print('db_error @find_user:', str(e))
        return None

def create_user(username=None, password=None, role='customer'):
    try:
        result = users.insert_one({
            'username': username,
            'password': password,
            'role': role,
            'created_at': datetime.now(),
            'favorite_products': [],
            'total_spent': 0
        })
        return str(result.inserted_id)
    except Exception as e:
        print('db_error @create_user:', str(e))

def list_product():
    try:
        products_list = []
        for product in products.find().sort('_id', -1):
            products_list.append({
                'id': str(product['_id']),
                'name': product['name'],
                'stock': product['stock'],
                'category': product['category']
            })
        return products_list
    except Exception as e:
        print('db_error @list_product:', str(e))
        return []

def create_order(user_id, products, total_amount):
    try:
        order = {
            'user_id': user_id,
            'products': products,
            'total_amount': total_amount,
            'status': 'pending',
            'created_at': datetime.now()
        }
        orders.insert_one(order)
        
        # Update user's total spent
        users.update_one(
            {'_id': user_id},
            {'$inc': {'total_spent': total_amount}}
        )
    except Exception as e:
        print('db_error @create_order:', str(e))

def get_customer_info(customer_id):
    try:
        # Convert customer_id to integer
        customer_id = int(customer_id)
        
        # Find customer by customer_id
        customer = customers.find_one({'customer_id': customer_id})
        if customer:
            # Calculate total spent from orders
            total_spent = 0
            orders_list = orders.find({'customer_id': customer_id})
            for order in orders_list:
                total_spent += order.get('total_price', 0)
            
            return {
                'id': str(customer['_id']),
                'name': customer.get('name', ''),
                'email': customer.get('email', ''),
                'phone': customer.get('phone', ''),
                'address': customer.get('address', ''),
                'created_at': customer.get('created_at', datetime.now()),
                'total_spent': total_spent
            }
        return None
    except Exception as e:
        print('db_error @get_customer_info:', str(e))
        return None

def get_customer_orders(customer_id, page=1, page_size=20):
    try:
        # Convert customer_id to integer
        customer_id = int(customer_id)
        
        # Get total count for pagination
        total_count = orders.count_documents({'customer_id': customer_id})
        
        # Calculate skip for pagination
        skip = (page - 1) * page_size
        
        # Get orders with pagination
        orders_list = orders.find({'customer_id': customer_id}) \
            .sort('created_at', -1) \
            .skip(skip) \
            .limit(page_size)
            
        # Format orders
        formatted_orders = []
        for order in orders_list:
            formatted_orders.append({
                'id': str(order.get('order_id')),
                'created_at': order.get('created_at', datetime.now()),
                'total_price': order.get('total_price', 0),
                'status': order.get('status', ''),
            })
            
        return {
            'orders': formatted_orders,
            'total_count': total_count
        }
    except Exception as e:
        print('db_error @get_customer_orders:', str(e))
        return {'orders': [], 'total_count': 0}

def get_order_info(order_id):
    try:
        # Find order by order_id
        order = orders.find_one({'order_id': int(order_id)})
        if order:
            # Get customer info
            customer = customers.find_one({'customer_id': order.get('customer_id')})
            customer_name = customer.get('name', '') if customer else ''
            
            return {
                'id': str(order.get('order_id')),
                'customer_name': customer_name,
                'created_at': order.get('created_at', datetime.now()),
                'status': order.get('status', ''),
                'total_price': order.get('total_price', 0),
                'note': order.get('note', '')
            }
        return None
    except Exception as e:
        print('db_error @get_order_info:', str(e))
        return None

def get_order_items(order_id):
    try:
        # Find order by order_id
        order = orders.find_one({'order_id': int(order_id)})
        if not order:
            return []
            
        # Get order items
        items = []
        for item in order.get('products', []):
            # Get product info
            product = products.find_one({'product_id': item.get('product_id')})
            if product:
                items.append({
                    'product_id': str(product.get('product_id')),
                    'product_name': product.get('name', ''),
                    'quantity': item.get('quantity', 0),
                    'unit_price': item.get('price', 0)
                })
        return items
    except Exception as e:
        print('db_error @get_order_items:', str(e))
        return []
