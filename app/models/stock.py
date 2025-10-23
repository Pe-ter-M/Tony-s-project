from app import db
from datetime import datetime

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    sku = db.Column(db.String(50), unique=True)  # Stock Keeping Unit
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    stock_ins = db.relationship('StockIn', backref='product', lazy=True, cascade='all, delete-orphan')
    stock_outs = db.relationship('StockOut', backref='product', lazy=True, cascade='all, delete-orphan')
    inventory = db.relationship('Inventory', backref='product', lazy=True, uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Product {self.name}>'

class StockIn(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    buying_cost = db.Column(db.Float, nullable=False)  # Cost per unit
    total_cost = db.Column(db.Float, nullable=False)  # quantity * buying_cost
    selling_price = db.Column(db.Float, nullable=False)  # Selling price per unit
    date_received = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    
    # Foreign Keys
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def calculate_total_cost(self):
        self.total_cost = self.quantity * self.buying_cost
    
    # def __repr__(self):
    #     return f'<StockIn {self.quantity} of {self.product.name}>'

class StockOut(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity_sold = db.Column(db.Integer, nullable=False)
    selling_price = db.Column(db.Float, nullable=False)  # Actual selling price
    total_sale = db.Column(db.Float, nullable=False)  # quantity_sold * selling_price
    profit = db.Column(db.Float, nullable=False)  # Auto-calculated profit
    date_sold = db.Column(db.DateTime, default=datetime.utcnow)
    customer_info = db.Column(db.String(200))
    notes = db.Column(db.Text)
    
    # Foreign Keys
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def calculate_profit(self, buying_cost):
        """Calculate profit based on buying cost and selling price"""
        self.profit = (self.selling_price - buying_cost) * self.quantity_sold
    
    def calculate_total_sale(self):
        self.total_sale = self.quantity_sold * self.selling_price
    
    # def __repr__(self):
    #     return f'<StockOut {self.quantity_sold} of {self.product.name}>'

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    current_quantity = db.Column(db.Integer, default=0)
    total_investment = db.Column(db.Float, default=0.0)  # Total money invested in current stock
    average_buying_cost = db.Column(db.Float, default=0.0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Key
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), unique=True, nullable=False)
    
    def update_stock_in(self, quantity, buying_cost):
        """Update inventory when stock comes in"""
        # Update average buying cost
        total_value = (self.current_quantity * self.average_buying_cost) + (quantity * buying_cost)
        self.current_quantity += quantity
        if self.current_quantity > 0:
            self.average_buying_cost = total_value / self.current_quantity
        self.total_investment = self.current_quantity * self.average_buying_cost
        self.last_updated = datetime.utcnow()
    
    def update_stock_out(self, quantity):
        """Update inventory when stock goes out"""
        if quantity <= self.current_quantity:
            self.current_quantity -= quantity
            self.total_investment = self.current_quantity * self.average_buying_cost
            self.last_updated = datetime.utcnow()
            return True
        return False
    
    def get_current_value(self):
        """Get current inventory value"""
        return self.current_quantity * self.average_buying_cost
    
    # def __repr__(self):
    #     return f'<Inventory {self.product.name}: {self.current_quantity} units>'