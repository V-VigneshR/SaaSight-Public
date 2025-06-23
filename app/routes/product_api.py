from flask import Blueprint, jsonify, abort, request
from flask_login import login_required
from app.models import db, Product

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([{
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'quantity': product.quantity,
        'seller': product.seller.username
    } for product in products])

@api.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get_or_404(id)
    return jsonify({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'quantity': product.quantity,
        'reviews': [{'id': r.id, 'text': r.text} for r in product.reviews]
    })

@api.route('/products', methods=['POST'])
@login_required
def add_product():
    data = request.get_json()

    if Product.query.filter_by(name=data['name']).first():
        return jsonify({'STATUS': 'error', 'message': 'Name already exists.'}), 409

    product = Product(
        name=data['name'],
        description=data.get('description', ''),
        price=float(data.get('price', 0)),
        quantity=int(data.get('quantity', 1)),
        seller_id=request.user.id  # optional: if you're storing seller info
    )
    db.session.add(product)
    db.session.commit()

    return jsonify({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'quantity': product.quantity
    }), 201
