from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from models import produto as ProdutoModel
from models import avaliacao as AvaliacaoModel

avaliacao_bp = Blueprint('avaliacao', __name__)

def verificar_login():
    return session.get('user_id') 

@avaliacao_bp.route('/produto/<int:produto_id>/avaliar', methods=['GET'])
def pagina_avaliar(produto_id):
    
    produto = ProdutoModel.buscar_produto_por_id(produto_id)
    
    if not produto:
        flash('Erro: Produto não encontrado.', 'erro')
        return redirect(url_for('vitrine.home'))

    avaliacoes, media_avaliacoes = AvaliacaoModel.buscar_avaliacoes_por_produto(produto_id)
    
    cliente_logado_id = verificar_login()
    
    for avaliacao in avaliacoes:
        avaliacao['pode_editar'] = (avaliacao['cliente_id'] == cliente_logado_id)
    
    return render_template('avaliacao.html', 
                           produto=produto,
                           avaliacoes=avaliacoes,
                           media_avaliacoes=media_avaliacoes,
                           username=session.get('username', 'Visitante') 
                          )


@avaliacao_bp.route('/produto/<int:produto_id>/enviar', methods=['POST'])
def enviar_avaliacao(produto_id):
    
    cliente_id = verificar_login()
    
    if not cliente_id:
        flash('Você precisa estar logado para enviar uma avaliação.', 'alerta')
        return redirect(url_for('auth.login')) 
    
    try:
        nota = int(request.form.get('nota'))
        comentario = request.form.get('comentario')
    except ValueError:
        flash('Erro: Nota inválida. Por favor, selecione uma nota de 1 a 5.', 'erro')
        return redirect(url_for('avaliacao.pagina_avaliar', produto_id=produto_id))
    
    if not 1 <= nota <= 5:
        flash('Erro: A nota deve estar entre 1 e 5 estrelas.', 'erro')
        return redirect(url_for('avaliacao.pagina_avaliar', produto_id=produto_id))
    
    sucesso = AvaliacaoModel.salvar_avaliacao(cliente_id, produto_id, nota, comentario)
    
    if sucesso:
        flash('Sua avaliação foi enviada com sucesso! Obrigado.', 'sucesso')
    else:
        flash('Erro: Não foi possível enviar sua avaliação. Tente novamente.', 'erro')
        
    return redirect(url_for('avaliacao.pagina_avaliar', produto_id=produto_id))


@avaliacao_bp.route('/avaliacao/<int:avaliacao_id>/editar', methods=['GET', 'POST'])
def editar_avaliacao(avaliacao_id):
    
    cliente_id = verificar_login()
    if not cliente_id:
        flash('Você precisa estar logado para editar uma avaliação.', 'alerta')
        return redirect(url_for('auth.login')) 

    avaliacao = AvaliacaoModel.buscar_avaliacao_por_id(avaliacao_id)
    
    if not avaliacao or avaliacao.cliente_id != cliente_id:
        flash('Acesso negado ou avaliação não encontrada.', 'erro')
        return redirect(url_for('vitrine.home'))
    
    if request.method == 'POST':
        nota = int(request.form.get('nota'))
        comentario = request.form.get('comentario')
        
        if AvaliacaoModel.atualizar_avaliacao(avaliacao_id, nota, comentario):
            flash('Avaliação atualizada com sucesso.', 'sucesso')
            return redirect(url_for('avaliacao.pagina_avaliar', produto_id=avaliacao.produto_id))
        else:
            flash('Erro ao atualizar a avaliação.', 'erro')
    
    return render_template('editar_avaliacao.html', avaliacao=avaliacao)


@avaliacao_bp.route('/avaliacao/<int:avaliacao_id>/excluir', methods=['POST'])
def excluir_avaliacao(avaliacao_id):
    
    cliente_id = verificar_login()
    if not cliente_id:
        flash('Você precisa estar logado para excluir uma avaliação.', 'alerta')
        return redirect(url_for('auth.login'))

    avaliacao = AvaliacaoModel.buscar_avaliacao_por_id(avaliacao_id)
    
    if not avaliacao or avaliacao.cliente_id != cliente_id:
        flash('Acesso negado ou avaliação não encontrada.', 'erro')
        return redirect(url_for('vitrine.home'))

    produto_id = avaliacao.produto_id
    
    if AvaliacaoModel.excluir_avaliacao(avaliacao_id):
        flash('Avaliação removida com sucesso.', 'sucesso')
    else:
        flash('Erro ao excluir a avaliação.', 'erro')

    return redirect(url_for('avaliacao.pagina_avaliar', produto_id=produto_id))
