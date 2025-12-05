# conexao.py
"""
Arquivo responsável por criar e devolver uma conexão com o banco MySQL.
Assim como no tutorial do professor, mantemos a criação da conexão em
um único lugar para reutilizar (boa prática).
"""
import mysql.connector
from mysql.connector import Error

def criar_conexao():
    """
    Tenta conectar ao MySQL e retorna o objeto de conexão.
    Se houver erro, imprime e retorna None.
    Ajuste host, user, password conforme seu XAMPP / MySQL local.
    """
    try:
        conexao = mysql.connector.connect(
            host="127.0.0.1",  
            port="7306",    # 'localhost' também funciona
            database="trabalho_login",
            user="root",            # usuário padrão do XAMPP
            password=""             # senha (se configurada no seu MySQL)
        )

        if conexao.is_connected():
            return conexao

    except Error as e:
        # Em ambiente real, logue em arquivo; aqui mostramos no console.
        print("Erro ao conectar ao MySQL:", e)

    return None
