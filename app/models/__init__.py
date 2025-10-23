from app import db, login_manager
from app.models.user import User
from app.models.product import Product,Inventory, StockIn, StockOut

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))