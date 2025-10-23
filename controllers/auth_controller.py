from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.cliente import Cliente

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        if not nome or not email or not senha:
            flash('Por favor, preencha todos os campos.', 'error')
            return redirect(url_for('auth.cadastro'))

        try:
            novo_cliente = Cliente(nome=nome, email=email, senha=senha)
            
            if novo_cliente.salvar():
                flash('Cadastro realizado com sucesso! Faça login.', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash('Erro ao cadastrar. O email pode já estar em uso.', 'error')
                return redirect(url_for('auth.cadastro'))
                
        except Exception as e:
            print(f"Erro interno no cadastro: {e}") 
            flash('Erro interno no cadastro. Tente novamente mais tarde.', 'error')
            return redirect(url_for('auth.cadastro'))
            
    return render_template('cadastro.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        if not email or not senha:
            flash('Por favor, insira email e senha.', 'error')
            return redirect(url_for('auth.login'))

        cliente_db = Cliente.buscar_por_email(email)
        
        if cliente_db and cliente_db.verificar_senha(senha):
            session['cliente_id'] = cliente_db.id
            session['cliente_nome'] = cliente_db.nome
            
            flash(f'Bem-vindo(a), {cliente_db.nome}!', 'success')
            
            return redirect(url_for('vitrine.home')) 
        else:
            flash('Email ou senha inválidos.', 'error')
            return redirect(url_for('auth.login'))
            
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.pop('cliente_id', None)
    session.pop('cliente_nome', None)
    session.pop('carrinho', None)
    session.modified = True 
    
    flash('Você saiu da sua conta. Volte logo!', 'info')
    return redirect(url_for('vitrine.home'))