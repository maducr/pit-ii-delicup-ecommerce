import psycopg2

def get_connection_params():
    return {
        "host": "localhost",
        "database": "delicup_db",
        "user": "projeto",
        "password": "Trabalhodafacul25",
        "port": "5432",
        "client_encoding": "utf8" 
    }

def get_db_connection():
    try:
        params = get_connection_params()
        conn = psycopg2.connect(**params)
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None