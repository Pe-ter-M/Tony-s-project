import os
from app import create_app, db
from app.models.user import User
from app.models.product import Product
from app.models.product import StockIn, StockOut, Inventory

config_name = os.environ.get('CONFIG_NAME')

app = create_app(config_name=config_name)

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Product': Product,
        'StockIn': StockIn,
        'StockOut': StockOut,
        'Inventory': Inventory
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)