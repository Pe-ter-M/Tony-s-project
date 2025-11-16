from app.models import StockOut, Product, db
def get_multi_product_sales():
    """Get all multi-product sales (headers only)"""
    sales = db.session.query(
        StockOut.sale_reference,
        StockOut.customer_name,
        StockOut.payment_method,
        StockOut.cash_amount,
        StockOut.mobile_money_amount,
        StockOut.date_sold,
        StockOut.total_sale,
        StockOut.profit,
        StockOut.user_id
    ).filter(
        StockOut.is_multi_product == True,
        StockOut.sale_reference.isnot(None)
    ).distinct(
        StockOut.sale_reference
    ).order_by(
        StockOut.date_sold.desc()
    ).all()
    
    return sales

def get_products_for_sale(sale_reference):
    """Get all products for a specific multi-product sale"""
    products = StockOut.query.filter_by(
        sale_reference=sale_reference
    ).join(Product).add_columns(
        Product.name,
        StockOut.quantity_sold,
        StockOut.selling_price,
        StockOut.total_sale,
        StockOut.profit
    ).all()
    
    return products

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