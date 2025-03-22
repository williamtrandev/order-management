from pymongo import MongoClient
from datetime import datetime

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
