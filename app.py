from flask import Flask, session
from controllers.vitrine_controller import vitrine_bp 
from controllers.auth_controller import auth_bp
from controllers.compra_controller import compra_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'uma_chave_secreta_e_complexa_para_seguranca_de_sessao' 
app.config['SESSION_TYPE'] = 'filesystem'

@app.context_processor
def inject_user_status():
    is_logged_in = 'cliente_id' in session
    
    return {
        'logged_in': is_logged_in,
        'username': session.get('cliente_nome'),
        'carrinho_count': len(session.get('carrinho', [])) if is_logged_in else 0
    }

app.register_blueprint(vitrine_bp)
app.register_blueprint(auth_bp, url_prefix='/auth') 
app.register_blueprint(compra_bp)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')