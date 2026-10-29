
# from flask import Flask, request, jsonify

# app = Flask(__name__)

# products = [
#     {"id": 1, "name": "Laptop", "category": "Electronics", "price": 55000, "stock": 10},
#     {"id": 2, "name": "Mouse", "category": "Electronics", "price": 500, "stock": 50},
#     {"id": 3, "name": "T-Shirt", "category": "Clothing", "price": 800, "stock": 20},
#     {"id": 4, "name": "Headphones", "category": "Electronics", "price": 1500, "stock": 15}
# ]


# # Get all products
# @app.route('/products', methods=['GET'])
# def get_products():
#     return jsonify({
#         'status': 'success',
#         'products': products
#     }), 200


# # Search product by name
# @app.route('/products/search', methods=['GET'])
# def search_product():
#     name = request.args.get('name', '').strip()

#     if not name:
#         return jsonify({
#             'status': 'error',
#             'msg': 'Please enter product name'
#         }), 400

#     result = [
#         p for p in products
#         if name.lower() in p['name'].lower()
#     ]

#     return jsonify({
#         'status': 'success',
#         'products': result
#     }), 200


# # Get product by ID
# @app.route('/products/<int:id>', methods=['GET'])
# def get_product_by_id(id):
#     for product in products:
#         if product['id'] == id:
#             return jsonify({
#                 'status': 'success',
#                 'product': product
#             }), 200

#     return jsonify({
#         'status': 'error',
#         'msg': 'Product ID not found'
#     }), 404


# # Get products by category
# @app.route('/products/category/<string:category>', methods=['GET'])
# def product_category(category):
#     result = [
#         p for p in products
#         if p['category'].lower() == category.lower()
#     ]

#     return jsonify({
#         'status': 'success',
#         'products': result
#     }), 200


from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Home page working!"

@app.route('/products', methods=['GET'])
def get_products():
    return jsonify({
        "status": "success",
        "products": [
            {"id": 1, "name": "Laptop"},
            {"id": 2, "name": "Mouse"}
        ]
    }), 200

if __name__ == "__main__":
    print(app.url_map)
    app.run(debug=True)




