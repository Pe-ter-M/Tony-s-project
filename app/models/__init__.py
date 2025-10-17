from app import db, login_manager
from app.models.user import User, Role
from app.models.product import Product, Category
from app.models.stock import StockIn, StockOut, Inventory

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))