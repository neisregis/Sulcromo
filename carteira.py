from flask import Flask, render_template
import mysql.connector
from config import config

app = Flask(__name__)

def obter_dados():
    try:
        # Conectar ao banco de dados
        conexao = mysql.connector.connect(**config)
        cursor = conexao.cursor()

        # Executar a consulta
        cursor.execute("SELECT * FROM VW_CONSULTA_GERAL vc")
        resultados = cursor.fetchall()

        # Fechar conexão
        cursor.close()
        conexao.close()

        # Retornar os resultados
        return resultados

    except mysql.connector.Error as err:
        print(f"Erro ao conectar ao banco de dados: {err}")
        return []

@app.route('/')
def index():
    # Obter dados da consulta
    dados = obter_dados()

    # Calcular as somas dos valores de "Valor Bruto" e "Valor Líquido", ignorando valores nulos
    total_valor_bruto = sum([row[8] for row in dados if row[8] is not None])  # Supondo que o "Valor Bruto" está na coluna 8
    total_valor_liquido = sum([row[9] for row in dados if row[9] is not None])  # Supondo que o "Valor Líquido" está na coluna 9

    # Renderizar os dados na página HTML, passando os totais
    return render_template('index.html', dados=dados, total_valor_bruto=total_valor_bruto, total_valor_liquido=total_valor_liquido)

if __name__ == '__main__':
    app.run(debug=True)
