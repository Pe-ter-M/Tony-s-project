from flask import render_template, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.product import Product, StockIn, StockOut, Inventory
from app.models.user import User
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from app.dashboard import dashboard_bp

@dashboard_bp.route('/')
@login_required
def index():
    """Main dashboard with comprehensive analytics"""
    
    # Date ranges for analytics
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Total metrics
    total_products = Product.query.count()
    total_inventory_value = db.session.query(func.sum(Inventory.current_quantity * Inventory.average_buying_cost)).scalar() or 0
    total_items_in_stock = db.session.query(func.sum(Inventory.current_quantity)).scalar() or 0
    
    # Sales metrics
    total_sales = db.session.query(func.sum(StockOut.total_sale)).scalar() or 0
    total_profit = db.session.query(func.sum(StockOut.profit)).scalar() or 0
    
    # Daily metrics
    daily_sales = db.session.query(func.sum(StockOut.total_sale)).filter(
        func.date(StockOut.date_sold) == today
    ).scalar() or 0
    
    daily_profit = db.session.query(func.sum(StockOut.profit)).filter(
        func.date(StockOut.date_sold) == today
    ).scalar() or 0
    
    # Weekly metrics
    weekly_sales = db.session.query(func.sum(StockOut.total_sale)).filter(
        StockOut.date_sold >= week_ago
    ).scalar() or 0
    
    weekly_profit = db.session.query(func.sum(StockOut.profit)).filter(
        StockOut.date_sold >= week_ago
    ).scalar() or 0
    
    # Monthly metrics
    monthly_sales = db.session.query(func.sum(StockOut.total_sale)).filter(
        StockOut.date_sold >= month_ago
    ).scalar() or 0
    
    monthly_profit = db.session.query(func.sum(StockOut.profit)).filter(
        StockOut.date_sold >= month_ago
    ).scalar() or 0
    
    # Stock movement
    stock_ins_this_month = db.session.query(func.sum(StockIn.quantity)).filter(
        StockIn.date_received >= month_ago
    ).scalar() or 0
    
    stock_outs_this_month = db.session.query(func.sum(StockOut.quantity_sold)).filter(
        StockOut.date_sold >= month_ago
    ).scalar() or 0
    
    # Top performing products (by quantity sold)
    top_products = db.session.query(
        Product.name,
        func.sum(StockOut.quantity_sold).label('total_sold'),
        func.sum(StockOut.profit).label('total_profit')
    ).join(StockOut).group_by(Product.id).order_by(desc('total_sold')).limit(5).all()
    
    # Least performing products
    least_products = db.session.query(
        Product.name,
        func.sum(StockOut.quantity_sold).label('total_sold'),
        func.sum(StockOut.profit).label('total_profit')
    ).join(StockOut).group_by(Product.id).order_by('total_sold').limit(5).all()
    
    # Low stock alerts (products with less than 10 items)
    low_stock_items = Inventory.query.filter(
        Inventory.current_quantity < 10,
        Inventory.current_quantity > 0
    ).join(Product).order_by(Inventory.current_quantity).all()
    
    # Out of stock items
    out_of_stock_items = Inventory.query.filter(
        Inventory.current_quantity == 0
    ).join(Product).all()
    
    # Recent transactions
    recent_sales = StockOut.query.join(Product).order_by(StockOut.date_sold.desc()).limit(10).all()
    recent_stock_ins = StockIn.query.join(Product).order_by(StockIn.date_received.desc()).limit(10).all()
    
    # Profit margin analysis
    profitable_products = db.session.query(
        Product.name,
        func.avg(StockOut.selling_price).label('avg_selling_price'),
        func.avg(Inventory.average_buying_cost).label('avg_buying_cost'),
        func.avg((StockOut.selling_price - Inventory.average_buying_cost) / StockOut.selling_price * 100).label('profit_margin')
    ).join(StockOut).join(Inventory).group_by(Product.id).having(
        func.count(StockOut.id) > 0
    ).order_by(desc('profit_margin')).limit(5).all()
    
    return render_template('dashboard/index.html',
                         total_products=total_products,
                         total_inventory_value=total_inventory_value,
                         total_items_in_stock=total_items_in_stock,
                         total_sales=total_sales,
                         total_profit=total_profit,
                         daily_sales=daily_sales,
                         daily_profit=daily_profit,
                         weekly_sales=weekly_sales,
                         weekly_profit=weekly_profit,
                         monthly_sales=monthly_sales,
                         monthly_profit=monthly_profit,
                         stock_ins_this_month=stock_ins_this_month,
                         stock_outs_this_month=stock_outs_this_month,
                         top_products=top_products,
                         least_products=least_products,
                         low_stock_items=low_stock_items,
                         out_of_stock_items=out_of_stock_items,
                         recent_sales=recent_sales,
                         recent_stock_ins=recent_stock_ins,
                         profitable_products=profitable_products)

@dashboard_bp.route('/api/sales-data')
@login_required
def sales_data():
    """API endpoint for sales chart data"""
    try:
        # Last 30 days sales data
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        print(f"Fetching sales data from {start_date} to {end_date}")
        
        daily_sales = db.session.query(
            func.date(StockOut.date_sold).label('date'),
            func.sum(StockOut.total_sale).label('sales'),
            func.sum(StockOut.profit).label('profit')
        ).filter(
            StockOut.date_sold >= start_date
        ).group_by(func.date(StockOut.date_sold)).order_by('date').all()
        
        print(f"Found {len(daily_sales)} days of sales data")
        
        # Fix: Handle both string and datetime date formats
        dates = []
        for sale in daily_sales:
            if hasattr(sale.date, 'strftime'):
                # It's a datetime object
                dates.append(sale.date.strftime('%Y-%m-%d'))
            else:
                # It's already a string, use it directly
                dates.append(str(sale.date))
        
        sales = [float(sale.sales or 0) for sale in daily_sales]
        profits = [float(sale.profit or 0) for sale in daily_sales]
        
        # Ensure we have data for all 30 days (fill missing days with zeros)
        all_dates = []
        all_sales = []
        all_profits = []
        
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            all_dates.append(date_str)
            
            # Find sales for this date
            if date_str in dates:
                index = dates.index(date_str)
                all_sales.append(sales[index])
                all_profits.append(profits[index])
            else:
                # No sales for this date
                all_sales.append(0.0)
                all_profits.append(0.0)
            
            current_date += timedelta(days=1)
        
        response_data = {
            'dates': all_dates,
            'sales': all_sales,
            'profits': all_profits
        }
        
        print(f"Returning data for {len(all_dates)} days")
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error in sales_data endpoint: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/api/product-performance')
@login_required
def product_performance():
    """API endpoint for product performance chart"""
    product_sales = db.session.query(
        Product.name,
        func.sum(StockOut.quantity_sold).label('quantity_sold'),
        func.sum(StockOut.total_sale).label('total_sales')
    ).join(StockOut).group_by(Product.id).order_by(desc('quantity_sold')).limit(10).all()
    
    product_names = [product.name for product in product_sales]
    quantities_sold = [int(product.quantity_sold or 0) for product in product_sales]
    total_sales = [float(product.total_sales or 0) for product in product_sales]
    
    return jsonify({
        'products': product_names,
        'quantities': quantities_sold,
        'sales': total_sales
    })