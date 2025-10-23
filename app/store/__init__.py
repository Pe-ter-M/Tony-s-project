from flask import Blueprint

store_bp = Blueprint('store', __name__)

from app.store import routes