import psycopg2
from config.db import get_connection_params
from models.item_pedido import ItemPedido

class Pedido:
    def __init__(self, id=None, id_cliente=None, status="Novo", 
                 metodo_pagamento=None, status_pagamento="Pendente"):
        self.id = id
        self.id_cliente = id_cliente
        self.status = status
        self.metodo_pagamento = metodo_pagamento
        self.status_pagamento = status_pagamento
        self.itens = []

    def adicionar_item(self, item: ItemPedido):
        self.itens.append(item)

    def salvar_transacional(self):
        conn = None
        try:
            conn = psycopg2.connect(**get_connection_params())
            cursor = conn.cursor()
            sql_pedido = """INSERT INTO Pedido (data, status, metodopagamento, statuspagamento, id_cliente) 
                            VALUES (NOW(), %s, %s, %s, %s) RETURNING id;"""
            values_pedido = (self.status, self.metodo_pagamento, self.status_pagamento, self.id_cliente)
            
            cursor.execute(sql_pedido, values_pedido)
            self.id = cursor.fetchone()[0]
            print(f"DEBUG: Pedido principal ID gerado: {self.id}")
            
            for item in self.itens:
                sql_item = """INSERT INTO ItemPedido (id_pedido, id_produto, quantidade, preco_unitario) 
                              VALUES (%s, %s, %s, %s);"""
                
                values_item = (self.id, item.id_produto, item.quantidade, item.preco_unitario)
            conn.commit()
            return True

        except Exception as e:
            if conn:
                conn.rollback()
            print(f"ERRO DE TRANSAÇÃO: {e}")
            return f"ERRO: {e}" 
            
        finally:
            if conn:
                cursor.close()
                conn.close()