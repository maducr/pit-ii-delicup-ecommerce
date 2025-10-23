from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.pedido import Pedido
from models.item_pedido import ItemPedido
from models.produto import Produto

compra_bp = Blueprint('compra', __name__)

@compra_bp.route('/adicionar_carrinho', methods=['POST'])
def adicionar_carrinho():
    if 'cliente_id' not in session:
        flash('Faça login para adicionar itens ao carrinho.', 'error')
        return redirect(url_for('auth.login'))
        
    try:
        id_produto = int(request.form.get('id_produto'))
        quantidade = int(request.form.get('quantidade', 1))
        preco_unitario = float(request.form.get('preco_unitario'))
        
    except (TypeError, ValueError):
        flash('Erro ao processar dados do produto. Tente novamente.', 'error')
        return redirect(url_for('vitrine.home'))

    carrinho = session.get('carrinho', [])
    item_existente = False
    
    for item in carrinho:
        if item['id_produto'] == id_produto:
            item['quantidade'] += quantidade 
            item_existente = True
            break
            
    if not item_existente:
        carrinho.append({
            'id_produto': id_produto,
            'quantidade': quantidade,
            'preco_unitario': preco_unitario
        })

    session['carrinho'] = carrinho
    session.modified = True 
    
    flash('Item adicionado ao carrinho!', 'success')
    return redirect(url_for('vitrine.home'))


@compra_bp.route('/carrinho')
def carrinho():
    if 'cliente_id' not in session:
        flash('Faça login para acessar seu carrinho.', 'error')
        return redirect(url_for('auth.login'))
        
    carrinho_itens_raw = session.get('carrinho', [])
    
    produtos_no_carrinho = []
    
    for item in carrinho_itens_raw:
        produto_db = Produto.buscar_por_id(item['id_produto']) 
        
        produtos_no_carrinho.append({
            'nome': produto_db.nome if produto_db else f"Produto ID {item['id_produto']}",
            'quantidade': item['quantidade'],
            'preco_unitario': item['preco_unitario'],
            'id_produto': item['id_produto']
        })
        
    return render_template('carrinho.html', carrinho=produtos_no_carrinho)

@compra_bp.route('/finalizar_compra', methods=['POST'])
def finalizar_compra():
    if 'cliente_id' not in session:
        flash('Você precisa estar logado para finalizar a compra.', 'error')
        return redirect(url_for('auth.login'))
        
    cliente_id = session.get('cliente_id')
    carrinho_itens = session.get('carrinho', [])
    
    if not carrinho_itens:
        flash('Seu carrinho está vazio.', 'error')
        return redirect(url_for('compra.carrinho'))

    try:
        novo_pedido = Pedido(
            id_cliente=cliente_id,
            metodo_pagamento="Cartão (Simulado)",
            status_pagamento="Aprovado"
        )
        
        for item_data in carrinho_itens:
             item = ItemPedido(
                 id_produto=item_data['id_produto'],
                 quantidade=item_data['quantidade'],
                 preco_unitario=item_data['preco_unitario']
             )
             novo_pedido.adicionar_item(item)

        
        if novo_pedido.salvar_transacional():
            session.pop('carrinho', None)
            session.modified = True 
            
            flash('Pedido finalizado com sucesso!', 'success')
            return redirect(url_for('compra.confirmacao', pedido_id=novo_pedido.id))
        else:
            flash('Falha ao processar o pedido. Estoque insuficiente ou erro interno.', 'error')
            return redirect(url_for('compra.carrinho'))
            
    except Exception as e:
        print(f"Erro CRÍTICO ao finalizar compra: {e}")
        flash("Ocorreu um erro interno ao processar a transação. Verifique o console.", 'error')
        return redirect(url_for('compra.carrinho'))


@compra_bp.route('/confirmacao/<int:pedido_id>')
def confirmacao(pedido_id):
    return render_template('confirmacao.html', pedido_id=pedido_id)