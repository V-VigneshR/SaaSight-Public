from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from app.models import db, Product, Review, CartItem, Order, OrderItem
from app.forms import ProductForm, ReviewForm
from app.utils.email import send_email

main = Blueprint('main', __name__)


@main.route('/')
def home():
    products = Product.query.all()
    return render_template('index.html', products=products)


@main.route('/<int:id>')
def product_detail(id):
    product = Product.query.get_or_404(id)
    return render_template('product.html', product=product)


@main.route('/<int:id>/reviews')
def get_reviews(id):
    product = Product.query.get_or_404(id)
    reviews = Review.query.filter_by(product_id=id).all()
    return render_template('review.html', product=product, reviews=reviews)


@main.route('/secured/addReview/<int:id>', methods=['GET', 'POST'])
@login_required
def add_review(id):
    if current_user.role == 'MANAGER':
        return render_template('error/permission-denied.html'), 403

    product = Product.query.get_or_404(id)
    form = ReviewForm()

    existing_review = Review.query.filter_by(product_id=id, user_id=current_user.id).first()
    if existing_review:
        flash("You've already submitted a review for this product.", "warning")
        return redirect(url_for('main.get_reviews', id=id))

    if form.validate_on_submit():
        review = Review(
            product_id=id,
            user_id=current_user.id,
            text=form.text.data,
            rating=form.rating.data,
            flagged=False
        )
        db.session.add(review)
        db.session.commit()
        flash('Review added successfully!', 'success')
        return redirect(url_for('main.get_reviews', id=id))

    return render_template('secured/addReview.html', product=product, form=form, review=None)


@main.route('/secured/addProduct', methods=['GET', 'POST'])
@login_required
def add_product():
    if current_user.role != 'MANAGER':
        flash("Only managers can add products.", "danger")
        return render_template('error/permission-denied.html'), 403

    form = ProductForm()

    if form.validate_on_submit():
        existing_product = Product.query.filter_by(name=form.name.data.strip()).first()
        if existing_product:
            flash('A product with that name already exists.', 'danger')
            return render_template('secured/addProduct.html', form=form)

        product = Product(
            name=form.name.data.strip(),
            description=form.description.data,
            price=form.price.data,
            quantity=form.quantity.data,
            seller_id=current_user.id
        )
        try:
            db.session.add(product)
            db.session.commit()
            flash('Product added successfully!', 'success')
            return redirect(url_for('main.home'))
        except IntegrityError:
            db.session.rollback()
            flash('Product name must be unique.', 'danger')

    return render_template('secured/addProduct.html', form=form)


@main.route('/secured')
@login_required
def secured():
    return render_template('secured/gateway.html')


@main.route('/user')
@login_required
def user_secured():
    if current_user.role not in ['USER', 'MANAGER']:
        return render_template('error/permission-denied.html'), 403
    return render_template('secured/user/index.html')


@main.route('/manager')
@login_required
def manager_secured():
    if current_user.role != 'MANAGER':
        return render_template('error/permission-denied.html'), 403
    return render_template('secured/manager/index.html')


@main.route('/secured/delete_review/<int:review_id>', methods=['POST'])
@login_required
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)

    if review.user_id != current_user.id and current_user.role != 'MANAGER':
        flash("You are not authorized to delete this review.", "danger")
        return render_template('error/permission-denied.html'), 403

    product_id = review.product_id
    db.session.delete(review)
    db.session.commit()
    flash('Review deleted successfully.', 'success')
    return redirect(url_for('main.get_reviews', id=product_id))


@main.route('/secured/edit_review/<int:review_id>', methods=['GET', 'POST'])
@login_required
def edit_review(review_id):
    review = Review.query.get_or_404(review_id)

    if current_user.id != review.user_id:
        return render_template('error/permission-denied.html'), 403

    form = ReviewForm(obj=review)
    if form.validate_on_submit():
        review.text = form.text.data
        review.rating = form.rating.data
        db.session.commit()
        flash('Review updated successfully!', 'success')
        return redirect(url_for('main.get_reviews', id=review.product_id))

    return render_template('secured/addReview.html', form=form, product=review.product, review=review)


@main.route('/secured/flag_review/<int:review_id>', methods=['POST'])
@login_required
def flag_review(review_id):
    try:
        review = Review.query.get_or_404(review_id)
        if review.user_id == current_user.id:
            flash("You can't flag your own review.", "warning")
            return redirect(request.referrer or url_for('main.home'))

        review.flagged = True
        review.flag_reason = request.form.get('reason') or "No reason provided."
        db.session.commit()
        flash("Review flagged for manager review.", "info")

    except Exception as e:
        db.session.rollback()
        print(f"⚠️ Flagging failed: {e}")
        flash("Something went wrong while flagging. Please try again.", "danger")

    return redirect(request.referrer or url_for('main.home'))


@main.route('/secured/manager/notifications')
@login_required
def view_notifications():
    if current_user.role != 'MANAGER':
        flash("You do not have permission to view this page.", "danger")
        return redirect(url_for('main.home'))

    flagged_reviews = Review.query.filter_by(flagged=True).all()
    return render_template("secured/manager/notifications.html", flagged_reviews=flagged_reviews)


@main.route('/secured/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get('quantity', 1))

    existing = CartItem.query.filter_by(user_id=current_user.id, product_id=product.id).first()
    if existing:
        existing.quantity += quantity
    else:
        cart_item = CartItem(user_id=current_user.id, product_id=product.id, quantity=quantity)
        db.session.add(cart_item)

    db.session.commit()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return {'status': 'success', 'message': 'Item added to cart.'}, 200

    flash("Item added to cart!", "success")
    return redirect(url_for('main.home'))


@main.route('/secured/cart')
@login_required
def view_cart():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    return render_template('cart.html', items=items)


@main.route('/secured/checkout', methods=['POST'])
@login_required
def checkout():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not items:
        flash("Your cart is empty.", "warning")
        return redirect(url_for('main.view_cart'))

    order = Order(user_id=current_user.id)
    db.session.add(order)
    db.session.flush()

    total = 0
    for item in items:
        product = Product.query.get(item.product_id)
        if item.quantity > product.quantity:
            flash(f"Not enough quantity for {product.name}", "danger")
            return redirect(url_for('main.view_cart'))

        product.quantity -= item.quantity
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=item.quantity,
            price=product.price
        )
        db.session.add(order_item)
        total += product.price * item.quantity

    db.session.query(CartItem).filter_by(user_id=current_user.id).delete()
    db.session.commit()

    # Send Email
    subject = "SaaSight Order Confirmation"
    body = f"Thanks for your order #{order.id}! Total: ₹{total:.2f}"
    send_email(subject, [current_user.username], body)

    flash("Order placed and confirmation email sent.", "success")
    return redirect(url_for('main.home'))
