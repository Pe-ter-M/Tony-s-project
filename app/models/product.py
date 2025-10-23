from app import db
from datetime import datetime

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    stock_ins = db.relationship('StockIn', backref='product', lazy=True, cascade='all, delete-orphan')
    stock_outs = db.relationship('StockOut', backref='product', lazy=True, cascade='all, delete-orphan')
    inventory = db.relationship('Inventory', backref='product', lazy=True, uselist=False, cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super(Product, self).__init__(**kwargs)
    
    def __repr__(self):
        return f'<Product {self.name}>'

class StockIn(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    buying_cost = db.Column(db.Float, nullable=False)  # Cost per unit when buying
    total_cost = db.Column(db.Float, nullable=False)  # quantity * buying_cost
    selling_price = db.Column(db.Float, nullable=False)  # Intended selling price
    date_received = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    
    # Foreign Keys
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __init__(self, **kwargs):
        super(StockIn, self).__init__(**kwargs) 

    def calculate_total_cost(self):
        self.total_cost = self.quantity * self.buying_cost
    
    def __repr__(self):
        prod = getattr(self, "product", None)
        name = getattr(prod, "name", "<no product>")
        return f'<StockIn {self.quantity} of {name}>'

class StockOut(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity_sold = db.Column(db.Integer, nullable=False)
    selling_price = db.Column(db.Float, nullable=False)  # Use existing selling_price column for actual sale price
    total_sale = db.Column(db.Float, nullable=False)  # quantity_sold * selling_price
    profit = db.Column(db.Float, nullable=False)  # Auto-calculated profit (selling_price - buying_cost) * quantity
    date_sold = db.Column(db.DateTime, default=datetime.utcnow)
    customer_info = db.Column(db.String(200))
    notes = db.Column(db.Text)
    
    # Foreign Keys
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __init__(self, **kwargs):
        super(StockOut, self).__init__(**kwargs) 

    def calculate_profit(self, buying_cost):
        """Calculate profit based on buying cost and selling price (SP - BP) * quantity"""
        self.profit = (self.selling_price - buying_cost) * self.quantity_sold
    
    def calculate_total_sale(self):
        self.total_sale = self.quantity_sold * self.selling_price
    
    def __repr__(self):
        prod = getattr(self, "product", None)
        name = getattr(prod, "name", "<no product>")
        return f'<StockOut {self.quantity_sold} of {name}>'

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    current_quantity = db.Column(db.Integer, default=0)
    total_investment = db.Column(db.Float, default=0.0)
    average_buying_cost = db.Column(db.Float, default=0.0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Key
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), unique=True, nullable=False)

    def __init__(self, **kwargs):
        super(Inventory, self).__init__(**kwargs) 

    def update_stock_in(self, quantity, buying_cost):
        """Update inventory when stock comes in"""
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

    def __repr__(self):
        prod = getattr(self, "product", None)
        name = getattr(prod, "name", "<no product>")
        return f'<Inventory {name}: {self.current_quantity} units>'
