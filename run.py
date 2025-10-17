import os
from app import create_app, db
from app.models.user import User
from app.models.product import Product, Category
from app.models.stock import StockIn, StockOut, Inventory

app = create_app(config_name='development')

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        # 'Role': Role,
        'Product': Product,
        'Category': Category,
        'StockIn': StockIn,
        'StockOut': StockOut,
        'Inventory': Inventory
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)