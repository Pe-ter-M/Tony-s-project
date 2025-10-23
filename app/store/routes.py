from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.product import Product, StockIn, StockOut, Inventory
from app.store.form import ProductForm, StockInForm, StockOutForm
from app.store import store_bp
from datetime import datetime

@store_bp.route('/')
@login_required
def index():
    """Store dashboard - shows current inventory"""
    inventory_items = Inventory.query.join(Product).order_by(Product.name).all()
    total_inventory_value = sum(item.get_current_value() for item in inventory_items)
    total_items = sum(item.current_quantity for item in inventory_items)
    
    return render_template('store/index.html',
                         inventory_items=inventory_items,
                         total_inventory_value=total_inventory_value,
                         total_items=total_items)

@store_bp.route('/products')
@login_required
def products():
    """Manage products"""
    products = Product.query.order_by(Product.name).all()
    return render_template('store/products.html', products=products)

@store_bp.route('/product/add', methods=['GET', 'POST'])
@login_required
def add_product():
    """Add new product"""
    form = ProductForm()
    
    if form.validate_on_submit():
        # Check if product name already exists
        existing_product = Product.query.filter_by(name=form.name.data).first()
        if existing_product:
            flash('Product with this name already exists!', 'error')
            return render_template('store/add_product.html', form=form)
        
        # Create new product
        product = Product(
            name=form.name.data,
            description=form.description.data
        )
        
        db.session.add(product)
        db.session.commit()
        
        # Create inventory record for the product
        inventory = Inventory(product_id=product.id)
        db.session.add(inventory)
        db.session.commit()
        
        flash(f'Product {product.name} added successfully!', 'success')
        return redirect(url_for('store.products'))
    
    return render_template('store/add_product.html', form=form)

@store_bp.route('/stock/in', methods=['GET', 'POST'])
@login_required
def stock_in():
    """Stock In - Add products to inventory"""
    form = StockInForm()
    
    # Populate product choices
    products = Product.query.order_by(Product.name).all()
    form.product_id.choices = [(p.id, p.name) for p in products]
    
    if form.validate_on_submit():
        product = Product.query.get(form.product_id.data)
        if not product:
            flash('Product not found!', 'error')
            return redirect(url_for('store.stock_in'))
        
        # Create stock in record
        stock_in = StockIn(
            product_id=form.product_id.data,
            quantity=form.quantity.data,
            buying_cost=form.buying_cost.data,
            selling_price=form.selling_price.data,
            notes=form.notes.data,
            user_id=current_user.id
        )
        stock_in.calculate_total_cost()
        
        # Update inventory
        inventory = Inventory.query.filter_by(product_id=product.id).first()
        if not inventory:
            inventory = Inventory(product_id=product.id)
            db.session.add(inventory)
        
        inventory.update_stock_in(stock_in.quantity, stock_in.buying_cost)
        
        db.session.add(stock_in)
        db.session.commit()
        
        flash(f'Stock added successfully for {product.name}!', 'success')
        return redirect(url_for('store.stock_in_history'))
    
    return render_template('store/stock_in.html', form=form)

@store_bp.route('/stock/in/history')
@login_required
def stock_in_history():
    """View stock in history"""
    stock_ins = StockIn.query.join(Product).order_by(StockIn.date_received.desc()).all()
    return render_template('store/stock_in_history.html', stock_ins=stock_ins)

@store_bp.route('/stock/out', methods=['GET', 'POST'])
@login_required
def stock_out():
    """Stock Out - Sell products (only show products with quantity > 0)"""
    form = StockOutForm()
    
    # Populate product choices with available stock (quantity > 0)
    products_with_stock = Product.query.join(Inventory).filter(Inventory.current_quantity > 0).order_by(Product.name).all()
    form.product_id.choices = [(p.id, f"{p.name} (Available: {p.inventory.current_quantity})") for p in products_with_stock]
    
    if form.validate_on_submit():
        product = Product.query.get(form.product_id.data)
        if not product:
            flash('Product not found!', 'error')
            return redirect(url_for('store.stock_out'))
        
        inventory = Inventory.query.filter_by(product_id=product.id).first()
        
        # Check if enough stock is available
        if inventory and inventory.current_quantity < form.quantity_sold.data:
            flash(f'Not enough stock! Only {inventory.current_quantity} units available.', 'error')
            return redirect(url_for('store.stock_out'))
        
        # Create stock out record
        stock_out = StockOut(
            product_id=form.product_id.data,
            quantity_sold=form.quantity_sold.data,
            selling_price=form.selling_price.data,  # This is the actual selling price
            customer_info=form.customer_info.data,
            notes=form.notes.data,
            user_id=current_user.id
        )
        stock_out.calculate_total_sale()
        if inventory:
            # Calculate profit: (Selling Price - Buying Cost) * Quantity
            stock_out.calculate_profit(inventory.average_buying_cost)
            
            # Update inventory
            inventory.update_stock_out(stock_out.quantity_sold)
        
        db.session.add(stock_out)
        db.session.commit()
        
        flash(f'Stock sold successfully for {product.name}! Profit: ${stock_out.profit:.2f}', 'success')
        return redirect(url_for('store.stock_out_history'))
    
    return render_template('store/stock_out.html', form=form)

@store_bp.route('/stock/out/history')
@login_required
def stock_out_history():
    """View stock out history"""
    stock_outs = StockOut.query.join(Product).order_by(StockOut.date_sold.desc()).all()
    total_profit = sum(so.profit for so in stock_outs)
    total_sales = sum(so.total_sale for so in stock_outs)
    
    return render_template('store/stock_out_history.html', 
                         stock_outs=stock_outs,
                         total_profit=total_profit,
                         total_sales=total_sales)

@store_bp.route('/api/product/<int:product_id>')
@login_required
def get_product_details(product_id):
    """API endpoint to get product details for AJAX calls"""
    product = Product.query.get_or_404(product_id)
    inventory = Inventory.query.filter_by(product_id=product_id).first()
    
    # Get the last intended selling price from stock_in
    last_stock_in = StockIn.query.filter_by(product_id=product_id).order_by(StockIn.date_received.desc()).first()
    
    return jsonify({
        'name': product.name,
        'current_stock': inventory.current_quantity if inventory else 0,
        'average_cost': inventory.average_buying_cost if inventory else 0,
        'last_selling_price': last_stock_in.selling_price if last_stock_in else 0
    })