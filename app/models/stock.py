from app import db
from datetime import datetime

class StockIn(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    unit_cost = db.Column(db.Float, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)
    reason = db.Column(db.String(200))
    reference = db.Column(db.String(100))  # PO number, etc.
    date_received = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    
    # Foreign Keys
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f'<StockIn {self.quantity} of Product {self.product_id}>'

class StockOut(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    reason = db.Column(db.String(200))  # Sale, damaged, etc.
    reference = db.Column(db.String(100))  # Sale ID, etc.
    date_issued = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    
    # Foreign Keys
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f'<StockOut {self.quantity} of Product {self.product_id}>'

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Key
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), unique=True, nullable=False)
    
    def update_stock(self, quantity_change, is_incoming=True):
        if is_incoming:
            self.quantity += quantity_change
        else:
            self.quantity -= quantity_change
        self.last_updated = datetime.utcnow()
    
    def __repr__(self):
        return f'<Inventory Product {self.product_id}: {self.quantity}>'