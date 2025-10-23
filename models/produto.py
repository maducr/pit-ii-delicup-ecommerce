from config.db import get_db_connection

class Produto:
    def __init__(self, id, nome, descricao, preco, estoque, media_avaliacoes=0.0):
        self.id = id
        self.nome = nome
        self.descricao = descricao
        self.preco = preco
        self.estoque = estoque
        self.media_avaliacoes = media_avaliacoes

    @staticmethod
    def buscar_todos():
        conn = get_db_connection()
        if conn is None:
            return []
        
        produtos = []
        try:
            with conn.cursor() as cur:
                sql = "SELECT id, nome, descricao, preco, estoque FROM Produto WHERE estoque > 0 ORDER BY nome"
                cur.execute(sql)
                
                for row in cur.fetchall():
                    produto = Produto(row[0], row[1], row[2], float(row[3]), row[4])
                    produtos.append(produto)
        except Exception as e:
            print(f"Erro ao buscar produtos: {e}")
        finally:
            if conn:
                conn.close()
        return produtos

    @staticmethod
    def buscar_por_id(id):
        conn = get_db_connection()
        if conn is None:
            return None
        
        produto = None
        try:
            with conn.cursor() as cur:
                sql = "SELECT id, nome, descricao, preco, estoque FROM Produto WHERE id = %s"
                cur.execute(sql, (id,))
                row = cur.fetchone()
                
                if row:
                    produto = Produto(row[0], row[1], row[2], float(row[3]), row[4])
        except Exception as e:
            print(f"Erro ao buscar produto por ID: {e}")
        finally:
            if conn:
                conn.close()
        return produto