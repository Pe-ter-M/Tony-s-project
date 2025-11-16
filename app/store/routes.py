# from flask import render_template, redirect, url_for, flash, request, jsonify
# import json
# from flask_login import login_required, current_user
# from app import db
# from app.models.product import Product, StockIn, StockOut, Inventory
# from app.store.form import ProductForm, StockInForm, StockOutForm
# from app.store import store_bp
# from datetime import datetime

# @store_bp.route('/')
# @login_required
# def index():
#     """Store dashboard - shows current inventory"""
#     inventory_items = Inventory.query.join(Product).order_by(Product.name).all()
#     total_inventory_value = sum(item.get_current_value() for item in inventory_items)
#     total_items = sum(item.current_quantity for item in inventory_items)
    
#     return render_template('store/index.html',
#                          inventory_items=inventory_items,
#                          total_inventory_value=total_inventory_value,
#                          total_items=total_items)

# @store_bp.route('/products')
# @login_required
# def products():
#     """Manage products"""
#     products = Product.query.order_by(Product.name).all()
#     return render_template('store/products.html', products=products)

# @store_bp.route('/product/add', methods=['GET', 'POST'])
# @login_required
# def add_product():
#     """Add new product"""
#     form = ProductForm()
    
#     if form.validate_on_submit():
#         # Check if product name already exists
#         existing_product = Product.query.filter_by(name=form.name.data).first()
#         if existing_product:
#             flash('Product with this name already exists!', 'error')
#             return render_template('store/add_product.html', form=form)
        
#         # Create new product
#         product = Product(
#             name=form.name.data,
#             description=form.description.data
#         )
        
#         db.session.add(product)
#         db.session.commit()
        
#         # Create inventory record for the product
#         inventory = Inventory(product_id=product.id)
#         db.session.add(inventory)
#         db.session.commit()
        
#         flash(f'Product {product.name} added successfully!', 'success')
#         return redirect(url_for('store.products'))
    
#     return render_template('store/add_product.html', form=form)

# @store_bp.route('/stock/in', methods=['GET', 'POST'])
# @login_required
# def stock_in():
#     """Stock In - Add products to inventory"""
#     form = StockInForm()
    
#     # Populate product choices
#     products = Product.query.order_by(Product.name).all()
#     form.product_id.choices = [(p.id, p.name) for p in products]
    
#     if form.validate_on_submit():
#         product = Product.query.get(form.product_id.data)
#         if not product:
#             flash('Product not found!', 'error')
#             return redirect(url_for('store.stock_in'))
        
#         # Create stock in record
#         stock_in = StockIn(
#             product_id=form.product_id.data,
#             quantity=form.quantity.data,
#             buying_cost=form.buying_cost.data,
#             selling_price=form.selling_price.data,
#             notes=form.notes.data,
#             user_id=current_user.id
#         )
#         stock_in.calculate_total_cost()
        
#         # Update inventory
#         inventory = Inventory.query.filter_by(product_id=product.id).first()
#         if not inventory:
#             inventory = Inventory(product_id=product.id)
#             db.session.add(inventory)
        
#         inventory.update_stock_in(stock_in.quantity, stock_in.buying_cost)
        
#         db.session.add(stock_in)
#         db.session.commit()
        
#         flash(f'Stock added successfully for {product.name}!', 'success')
#         return redirect(url_for('store.stock_in_history'))
    
#     return render_template('store/stock_in.html', form=form)

# @store_bp.route('/stock/in/history')
# @login_required
# def stock_in_history():
#     """View stock in history"""
#     stock_ins = StockIn.query.join(Product).order_by(StockIn.date_received.desc()).all()
#     return render_template('store/stock_in_history.html', stock_ins=stock_ins)

# @store_bp.route('/stock/out', methods=['GET', 'POST'])
# @login_required
# def stock_out():
#     """
#     Stock Out endpoint for selling single or multiple products
#     Supports multiple payment methods: cash, mobile_money, or both
#     """
    
#     if request.method == 'POST':
#         try:
#             # Get JSON data from frontend
#             data = request.get_json()
            
#             if not data:
#                 return jsonify({'error': 'No data provided'}), 400
            
#             # Extract main form data
#             customer_name = data.get('customer_name', 'Customer X')
#             payment_method = data.get('payment_method')
#             cash_amount = data.get('cash_amount', 0)
#             mobile_money_amount = data.get('mobile_money_amount', 0)
#             products = data.get('products', [])
            
#             # Validate required fields
#             if not payment_method:
#                 return jsonify({'error': 'Payment method is required'}), 400
            
#             if not products:
#                 return jsonify({'error': 'At least one product is required'}), 400
            
#             # Validate payment amounts based on payment method
#             if payment_method == 'cash':
#                 if cash_amount <= 0:
#                     return jsonify({'error': 'Cash amount must be greater than 0 for cash payment'}), 400
#                 mobile_money_amount = 0  # Ensure mobile money is 0 for cash only
                
#             elif payment_method == 'mobile_money':
#                 if mobile_money_amount <= 0:
#                     return jsonify({'error': 'Mobile money amount must be greater than 0 for mobile money payment'}), 400
#                 cash_amount = 0  # Ensure cash is 0 for mobile money only
                
#             elif payment_method == 'both':
#                 if cash_amount <= 0 or mobile_money_amount <= 0:
#                     return jsonify({'error': 'Both cash and mobile money amounts must be greater than 0 for combined payment'}), 400
                
#                 # Validate that total payment matches product totals
#                 total_product_value = sum(float(product['total_price']) for product in products)
#                 total_payment = float(cash_amount) + float(mobile_money_amount)
                
#                 if abs(total_payment - total_product_value) > 0.01:  # Allow small floating point differences
#                     return jsonify({'error': f'Total payment ({total_payment}) does not match total product value ({total_product_value})'}), 400
            
#             # Print all received data (as requested)
#             print("\n" + "="*50)
#             print("STOCK OUT SUBMISSION RECEIVED")
#             print("="*50)
#             print(f"Customer Name: {customer_name}")
#             print(f"Payment Method: {payment_method}")
#             print(f"Cash Amount: KES {cash_amount:.2f}")
#             print(f"Mobile Money Amount: KES {mobile_money_amount:.2f}")
#             print(f"Total Payment: KES {(float(cash_amount) + float(mobile_money_amount)):.2f}")
#             print("\nPRODUCTS:")
#             print("-" * 30)
            
#             total_quantity = 0
#             total_value = 0
            
#             for i, product in enumerate(products, 1):
#                 product_id = product.get('product_id')
#                 product_name = product.get('product_name', 'Unknown Product')
#                 quantity = product.get('quantity', 0)
#                 selling_price = product.get('selling_price', 0)
#                 total_price = product.get('total_price', 0)
                
#                 print(f"{i}. {product_name}")
#                 print(f"   Product ID: {product_id}")
#                 print(f"   Quantity: {quantity}")
#                 print(f"   Selling Price: KES {selling_price:.2f}")
#                 print(f"   Total: KES {total_price:.2f}")
#                 print()
                
#                 total_quantity += int(quantity)
#                 total_value += float(total_price)
            
#             print("SUMMARY:")
#             print(f"Total Products: {len(products)}")
#             print(f"Total Quantity: {total_quantity}")
#             print(f"Total Value: KES {total_value:.2f}")
#             print("="*50)
#             print("\n")
            
#             # Return success response
#             return jsonify({
#                 'success': True,
#                 'message': f'Stock out recorded successfully for {len(products)} product(s)',
#                 'data': {
#                     'customer_name': customer_name,
#                     'payment_method': payment_method,
#                     'cash_amount': cash_amount,
#                     'mobile_money_amount': mobile_money_amount,
#                     'total_payment': float(cash_amount) + float(mobile_money_amount),
#                     'total_products': len(products),
#                     'total_quantity': total_quantity,
#                     'total_value': total_value
#                 }
#             }), 200
            
#         except Exception as e:
#             print(f"Error processing stock out: {str(e)}")
#             return jsonify({'error': 'Internal server error'}), 500
    
#     else:
#         # GET request - populate form with available products
#         products_with_stock = Product.query.join(Inventory).filter(
#             Inventory.current_quantity > 0
#         ).order_by(Product.name).all()
        
#         products_data = []
#         for product in products_with_stock:
#             products_data.append({
#                 'id': product.id,
#                 'name': product.name,
#                 'current_stock': product.inventory.current_quantity,
#                 'average_cost': float(product.inventory.average_buying_cost),
#                 'suggested_price': float(product.inventory.average_buying_cost) * 1.2  # 20% markup as default
#             })
        
#         return jsonify({'products': products_data})

# # API endpoint to get individual product details
# # @store_bp.route('/api/product/<int:product_id>', methods=['GET'])
# # @login_required
# # def get_product_details(product_id):
# #     """Get detailed information for a specific product"""
# #     product = Product.query.get_or_404(product_id)
    
# #     return jsonify({
# #         'id': product.id,
# #         'name': product.name,
# #         'current_stock': product.inventory.current_quantity,
# #         'average_cost': float(product.inventory.average_buying_cost),
# #         'suggested_price': float(product.inventory.average_buying_cost) * 1.2  # 20% markup
# #     })



# @store_bp.route('/stock/out/history')
# @login_required
# def stock_out_history():
#     """View stock out history"""
#     stock_outs = StockOut.query.join(Product).order_by(StockOut.date_sold.desc()).all()
#     total_profit = sum(so.profit for so in stock_outs)
#     total_sales = sum(so.total_sale for so in stock_outs)
    
#     # Add buying price data to each stock_out
#     for stock_out in stock_outs:
#         inventory = Inventory.query.filter_by(product_id=stock_out.product_id).first()
#         if inventory:
#             stock_out.buying_price = inventory.average_buying_cost
#         else:
#             stock_out.buying_price = 0
    
#     return render_template('store/stock_out_history.html', 
#                          stock_outs=stock_outs,
#                          total_profit=total_profit,
#                          total_sales=total_sales)

# @store_bp.route('/api/product/<int:product_id>')
# @login_required
# def get_product_details(product_id):
#     """API endpoint to get product details for AJAX calls"""
#     product = Product.query.get_or_404(product_id)
#     inventory = Inventory.query.filter_by(product_id=product_id).first()
    
#     # Get the last intended selling price from stock_in
#     last_stock_in = StockIn.query.filter_by(product_id=product_id).order_by(StockIn.date_received.desc()).first()
    
#     return jsonify({
#         'name': product.name,
#         'current_stock': inventory.current_quantity if inventory else 0,
#         'average_cost': inventory.average_buying_cost if inventory else 0,
#         'last_selling_price': last_stock_in.selling_price if last_stock_in else 0
#     })

# @store_bp.route('/receipt/<int:stock_out_id>')
# @login_required
# def receipt(stock_out_id):
#     """Generate receipt for a specific sale"""
#     stock_out = StockOut.query.get_or_404(stock_out_id)
    
#     return render_template('store/receipt.html', 
#                          stock_out=stock_out,
#                          shop_name="TONIS SUPPLIERS SHOP",
#                          shop_location="Motel Building Next to Silent Lodge",
#                          shop_phone="+254 7XX XXX XXX",
#                          shop_email="info@tonissuppliers.com")





from flask import render_template, redirect, url_for, flash, request, jsonify
import json
from flask_login import login_required, current_user
from app import db
from app.models.product import Product, StockIn, StockOut, Inventory
from app.store.form import ProductForm, StockInForm, StockOutForm
from app.store import store_bp
from app.util.helpers import get_multi_product_sales
from datetime import datetime
from app.models.user import User

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
    """
    Stock Out - Sell products with multiple product support
    Uses extended StockOut model for both single and multi-product sales
    """
    form = StockOutForm()
    
    # Populate product choices with available stock
    products_with_stock = Product.query.join(Inventory).filter(
        Inventory.current_quantity > 0
    ).order_by(Product.name).all()
    
    form.product_id.choices = [(0, 'Select a product')] + [
        (p.id, f"{p.name} (Stock: {p.inventory.current_quantity})") 
        for p in products_with_stock
    ]
    
    if request.method == 'POST':
        try:
            # Get form data
            customer_name = request.form.get('customer_name', 'Customer X')
            payment_method = request.form.get('payment_method')
            cash_amount = float(request.form.get('cash_amount', 0))
            mobile_money_amount = float(request.form.get('mobile_money_amount', 0))
            product_data_json = request.form.get('product_data')
            
            print(f"\n=== STOCK OUT FORM DATA RECEIVED ===")
            print(f"Customer: {customer_name}")
            print(f"Payment Method: {payment_method}")
            print(f"Cash Amount: {cash_amount}")
            print(f"Mobile Money Amount: {mobile_money_amount}")
            print(f"Product Data JSON: {product_data_json}")
            print("====================================\n")
            
            # Validate required fields
            if not payment_method:
                flash('Payment method is required!', 'error')
                return redirect(url_for('store.stock_out'))
            
            if not product_data_json:
                flash('No products selected!', 'error')
                return redirect(url_for('store.stock_out'))
            
            try:
                products = json.loads(product_data_json)
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                flash('Invalid product data!', 'error')
                return redirect(url_for('store.stock_out'))
            
            # Validate we have products
            if not products:
                flash('No products selected!', 'error')
                return redirect(url_for('store.stock_out'))
            
            # Validate payment amounts based on payment method
            total_product_value = sum(float(product['total_price']) for product in products)
            
            if payment_method == 'cash':
                if cash_amount <= 0:
                    flash('Cash amount must be greater than 0 for cash payment', 'error')
                    return redirect(url_for('store.stock_out'))
                mobile_money_amount = 0
                
            elif payment_method == 'mobile_money':
                if mobile_money_amount <= 0:
                    flash('Mobile money amount must be greater than 0 for mobile money payment', 'error')
                    return redirect(url_for('store.stock_out'))
                cash_amount = 0
                
            elif payment_method == 'both':
                if cash_amount <= 0 or mobile_money_amount <= 0:
                    flash('Both cash and mobile money amounts must be greater than 0 for combined payment', 'error')
                    return redirect(url_for('store.stock_out'))
                
                total_payment = cash_amount + mobile_money_amount
                
                if abs(total_payment - total_product_value) > 0.01:
                    flash(f'Total payment (KES {total_payment:.2f}) does not match total product value (KES {total_product_value:.2f})', 'error')
                    return redirect(url_for('store.stock_out'))
            
            # Generate unique sale reference for multi-product sales
            sale_reference = None
            if len(products) > 1:
                sale_reference = f"SALE-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
            
            total_quantity = 0
            total_value = 0
            total_profit = 0
            
            print(f"\n{'='*60}")
            print("PROCESSING STOCK OUT - SAVING TO DATABASE")
            print(f"{'='*60}")
            print(f"Sale Reference: {sale_reference}")
            print(f"Customer: {customer_name}")
            print(f"Payment Method: {payment_method}")
            print(f"Cash: KES {cash_amount:.2f}")
            print(f"Mobile Money: KES {mobile_money_amount:.2f}")
            print(f"{'-'*60}")
            
            # Process each product in the sale
            for i, product_data in enumerate(products, 1):
                product_id = product_data.get('product_id')
                quantity = int(product_data.get('quantity', 0))
                selling_price = float(product_data.get('selling_price', 0))
                total_price = float(product_data.get('total_price', 0))
                
                # Get product and inventory
                product = Product.query.get(product_id)
                if not product:
                    print(f"ERROR: Product ID {product_id} not found!")
                    flash(f'Product ID {product_id} not found!', 'error')
                    continue
                
                inventory = Inventory.query.filter_by(product_id=product_id).first()
                if not inventory:
                    print(f"ERROR: No inventory found for product {product.name}!")
                    flash(f'No inventory found for {product.name}!', 'error')
                    continue
                
                # Check stock availability
                if inventory.current_quantity < quantity:
                    print(f"ERROR: Insufficient stock for {product.name}. Available: {inventory.current_quantity}, Requested: {quantity}")
                    flash(f'Insufficient stock for {product.name}! Available: {inventory.current_quantity}', 'error')
                    continue
                
                # Calculate profit
                buying_cost = inventory.average_buying_cost
                profit = (selling_price - buying_cost) * quantity
                
                # Create StockOut record
                stock_out = StockOut(
                    product_id=product_id,
                    quantity_sold=quantity,
                    selling_price=selling_price,
                    total_sale=total_price,
                    profit=profit,
                    user_id=current_user.id,
                    # Multi-product fields
                    sale_reference=sale_reference,
                    is_multi_product=(len(products) > 1),
                    customer_name=customer_name,
                    payment_method=payment_method,
                    cash_amount=cash_amount if i == 1 else 0,  # Only store in first record
                    mobile_money_amount=mobile_money_amount if i == 1 else 0  # Only store in first record
                )
                
                # Update inventory
                inventory.update_stock_out(quantity)
                
                db.session.add(stock_out)
                
                # Update totals
                total_quantity += quantity
                total_value += total_price
                total_profit += profit
                
                # Print product details
                print(f"{i}. {product.name}")
                print(f"   - Quantity: {quantity}")
                print(f"   - Selling Price: KES {selling_price:.2f}")
                print(f"   - Total: KES {total_price:.2f}")
                print(f"   - Cost: KES {buying_cost:.2f}")
                print(f"   - Profit: KES {profit:.2f}")
                print(f"   - Stock After: {inventory.current_quantity}")
            
            # Print summary
            print(f"{'='*60}")
            print("SALE SUMMARY:")
            print(f"Total Products: {len(products)}")
            print(f"Total Quantity: {total_quantity}")
            print(f"Total Value: KES {total_value:.2f}")
            print(f"Total Profit: KES {total_profit:.2f}")
            print(f"Sale Type: {'Multi-Product' if len(products) > 1 else 'Single Product'}")
            print(f"{'='*60}")
            
            # Commit all changes
            db.session.commit()
            
            # Flash success message
            if len(products) > 1:
                flash(f'Multi-product sale completed successfully! Sale #{sale_reference}', 'success')
            else:
                product_name = Product.query.get(products[0]['product_id']).name
                flash(f'Sale completed successfully for {product_name}!', 'success')
            
            return redirect(url_for('store.stock_out'))
            
        except Exception as e:
            db.session.rollback()
            print(f"ERROR processing stock out: {str(e)}")
            import traceback
            traceback.print_exc()
            flash(f'Error processing stock out: {str(e)}', 'error')
            return redirect(url_for('store.stock_out'))
    
    # GET request - render the stock out form
    return render_template('store/stock_out.html', form=form)



# FIXED: Renamed this endpoint to avoid conflict
@store_bp.route('/api/product-details/<int:product_id>')
@login_required
def get_product_details_api(product_id):
    """API endpoint to get product details for AJAX calls"""
    product = Product.query.get_or_404(product_id)
    inventory = Inventory.query.filter_by(product_id=product_id).first()
    
    # Get the last intended selling price from stock_in
    last_stock_in = StockIn.query.filter_by(product_id=product_id).order_by(StockIn.date_received.desc()).first()
    
    return jsonify({
        'name': product.name,
        'current_stock': inventory.current_quantity if inventory else 0,
        'average_cost': inventory.average_buying_cost if inventory else 0,
        'last_selling_price': last_stock_in.selling_price if last_stock_in else 0,
        'suggested_price': inventory.average_buying_cost * 1.2 if inventory else 0  # 20% markup
    })


@store_bp.route('/stock/out/history')
@login_required
def stock_out_history():
    """View stock out history - both single and multi-product sales"""
    
    # Single product sales
    single_sales = StockOut.query.filter_by(
        is_multi_product=False
    ).join(Product).join(User).order_by(
        StockOut.date_sold.desc()
    ).all()
    
    # Multi-product sales - use subquery to get headers
    from sqlalchemy import func
    
    # Subquery to get the first ID for each sale reference
    subquery = db.session.query(
        func.min(StockOut.id).label('min_id')
    ).filter(
        StockOut.is_multi_product == True,
        StockOut.sale_reference.isnot(None)
    ).group_by(StockOut.sale_reference).subquery()
    
    # Get the header records using the min IDs
    multi_sales = StockOut.query.join(
        subquery, StockOut.id == subquery.c.min_id
    ).join(User).order_by(StockOut.date_sold.desc()).all()
    
    # Calculate totals
    total_single_sales = sum(sale.total_sale for sale in single_sales)
    total_single_profit = sum(sale.profit for sale in single_sales)
    
    total_multi_sales = sum(sale.total_sale for sale in multi_sales)
    total_multi_profit = sum(sale.profit for sale in multi_sales)
    
    total_all_sales = total_single_sales + total_multi_sales
    total_all_profit = total_single_profit + total_multi_profit
    
    return render_template('store/stock_out_history.html',
                         single_sales=single_sales,
                         multi_sales=multi_sales,
                         total_sales=total_all_sales,
                         total_profit=total_all_profit,
                         get_sale_totals=get_sale_totals)

@store_bp.route('/receipt/<int:stock_out_id>')
@login_required
def receipt(stock_out_id):
    """Generate receipt for a single product sale"""
    stock_out = StockOut.query.get_or_404(stock_out_id)
    
    return render_template('store/receipt.html', 
                         stock_out=stock_out,
                         shop_name="TONIS SUPPLIERS SHOP",
                         shop_location="Motel Building Next to Silent Lodge",
                         shop_phone="+254 7XX XXX XXX",
                         shop_email="info@tonissuppliers.com")

@store_bp.route('/receipt/sale/<sale_reference>')
@login_required
def multi_product_receipt(sale_reference):
    """Generate receipt for a multi-product sale"""
    # Get all products in this sale
    sale_products = StockOut.query.filter_by(
        sale_reference=sale_reference
    ).join(Product).join(User).all()
    
    if not sale_products:
        flash('Sale not found!', 'error')
        return redirect(url_for('store.stock_out_history'))
    
    # Get sale header info (first product in the sale)
    sale_header = sale_products[0]
    
    # Calculate totals
    totals = get_sale_totals(sale_reference)
    
    return render_template('store/multi_product_receipt.html',
                         sale_header=sale_header,
                         products=sale_products,
                         totals=totals,
                         shop_name="TONIS SUPPLIERS SHOP",
                         shop_location="Motel Building Next to Silent Lodge",
                         shop_phone="+254 7XX XXX XXX",
                         shop_email="info@tonissuppliers.com",
                         now=datetime.utcnow())

def get_sale_totals(sale_reference):
    """Calculate totals for a multi-product sale"""
    products = StockOut.query.filter_by(sale_reference=sale_reference).all()
    
    totals = {
        'quantity': sum(p.quantity_sold for p in products),
        'amount': sum(p.total_sale for p in products),
        'profit': sum(p.profit for p in products),
        'product_count': len(products)
    }
    
    return totals