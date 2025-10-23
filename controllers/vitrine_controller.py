from flask import Blueprint, render_template
from models.produto import Produto

vitrine_bp = Blueprint('vitrine', __name__)

@vitrine_bp.route('/')
def home():
    produtos = Produto.buscar_todos()
    
    return render_template('vitrine.html', produtos=produtos)