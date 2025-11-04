from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, IntegerField, FloatField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional, Length

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Add Product')

class StockInForm(FlaskForm):
    product_id = SelectField('Product', coerce=int, validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    buying_cost = FloatField('Buying Cost per Unit (KES)', validators=[DataRequired(), NumberRange(min=0.01)])
    selling_price = FloatField('Intended Selling Price (KES)', validators=[DataRequired(), NumberRange(min=0.01)])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Add Stock')

class StockOutForm(FlaskForm):
    product_id = SelectField('Product', coerce=int, validators=[DataRequired()])
    quantity_sold = IntegerField('Quantity Sold', validators=[DataRequired(), NumberRange(min=1)])
    selling_price = FloatField('Selling Price (KES)', validators=[DataRequired(), NumberRange(min=0.01)])
    customer_info = StringField('Customer Info', validators=[Optional(), Length(max=200)])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Sell Stock')