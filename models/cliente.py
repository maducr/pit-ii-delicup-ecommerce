import psycopg2
import bcrypt
from config.db import get_connection_params

class Cliente:
    def __init__(self, id=None, nome=None, email=None, senha=None):
        self.id = id
        self.nome = nome
        self.email = email
        self.senha = senha 

    def salvar(self):
        conn = None
        try:
            senha_bytes = self.senha.encode('utf-8')
            hashed_senha = bcrypt.hashpw(senha_bytes, bcrypt.gensalt())
            
            conn = psycopg2.connect(**get_connection_params())
            cursor = conn.cursor()
            
            sql = """INSERT INTO Cliente (nome, email, senha) 
                     VALUES (%s, %s, %s) RETURNING id;"""
            values = (self.nome, self.email, hashed_senha.decode('utf-8'))
            
            cursor.execute(sql, values)
            
            self.id = cursor.fetchone()[0]
            conn.commit()
            return True
        except psycopg2.IntegrityError:
            print("Erro: E-mail já cadastrado.")
            return False
        except (Exception, psycopg2.Error) as error:
            print(f"Erro ao salvar Cliente: {error}")
            return False
        finally:
            if conn:
                cursor.close()
                conn.close()

    @staticmethod
    def buscar_por_email(email):
        conn = None
        try:
            conn = psycopg2.connect(**get_connection_params())
            cursor = conn.cursor()
            
            sql = "SELECT id, nome, email, senha FROM Cliente WHERE email = %s;"
            cursor.execute(sql, (email,))
            
            row = cursor.fetchone()
            if row:
                cliente = Cliente(id=row[0], nome=row[1], email=row[2], senha=row[3])
                return cliente
            return None
            
        except (Exception, psycopg2.Error) as error:
            print(f"Erro ao buscar Cliente por email: {error}")
            return None
        finally:
            if conn:
                cursor.close()
                conn.close()

    def verificar_senha(self, senha_texto_puro):
        try:
            return bcrypt.checkpw(
                senha_texto_puro.encode('utf-8'), 
                self.senha.encode('utf-8')
            )
        except:
            return False

if __name__ == '__main__':
    print("--- Teste 1: Cadastro e Persistência ---")

    TEST_EMAIL = "teste@cookiedelicia.com"
    TEST_SENHA = "senhasegura123"
    
    novo_cliente = Cliente(
        nome="Cliente Teste", 
        email=TEST_EMAIL, 
        senha=TEST_SENHA
    )
    
    if novo_cliente.salvar():
        print(f"Sucesso! Cliente cadastrado com ID: {novo_cliente.id}")
        
        print("\n--- Teste 2: Busca por Email e Verificação de Senha ---")
        
        cliente_do_db = Cliente.buscar_por_email(TEST_EMAIL)
        
        if cliente_do_db:
            print(f"Busca OK. Nome no DB: {cliente_do_db.nome}")
            
            if cliente_do_db.verificar_senha(TEST_SENHA):
                print("Autenticação OK! Senha em texto puro corresponde ao Hash.")
            else:
                print("ERRO CRÍTICO: Falha na verificação de senha (Hash incorreto ou comparação falhou).")
                
        else:
            print(f"ERRO: Cliente com email {TEST_EMAIL} não foi encontrado no DB.")
            
    else:
        print("FALHA CRÍTICA: Não foi possível salvar o cliente no banco de dados.")