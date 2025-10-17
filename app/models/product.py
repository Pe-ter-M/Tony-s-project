from app import db
from datetime import datetime

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    products = db.relationship('Product', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    sku = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    cost_price = db.Column(db.Float, nullable=False)
    reorder_level = db.Column(db.Integer, default=10)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    
    # Relationships
    stock_ins = db.relationship('StockIn', backref='product', lazy=True)
    stock_outs = db.relationship('StockOut', backref='product', lazy=True)
    inventory = db.relationship('Inventory', backref='product', lazy=True, uselist=False)
    
    @property
    def current_stock(self):
        if self.inventory:
            return self.inventory.quantity
        return 0
    
    @property
    def stock_value(self):
        return self.current_stock * self.cost_price
    
    def __repr__(self):
        return f'<Product {self.name} (SKU: {self.sku})>'