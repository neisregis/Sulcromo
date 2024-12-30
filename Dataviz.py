import streamlit as st
import pandas as pd
from aba1 import exibir_aba1
from aba2 import exibir_aba2
from aba3 import exibir_aba3
from aba4 import exibir_aba4
from aba5 import exibir_aba5
import mysql.connector

# Função para obter dados do banco de dados
from config import config

# Função para obter dados a partir do banco de dados
def obter_dados():
    try:
        conexao = mysql.connector.connect(**config())  # Passa os parâmetros do dicionário corretamente
        cursor = conexao.cursor()
        
        # Ajuste na consulta SQL para incluir as novas colunas
        cursor.execute("SELECT * FROM VW_CONSULTA_GERAL vc")
        resultados = cursor.fetchall()
        cursor.close()
        conexao.close()
        return resultados
    except Exception as e:
        st.error(f"Erro ao obter dados: {e}")
        return []

# Aplicação principal
def main():
    st.set_page_config(layout="wide")  # Define o layout para preencher toda a largura

    # Carregar e exibir o logotipo no canto superior direito
    col1, col2 = st.columns([8, 1])  # Ajuste para layout: 8/1, com logotipo na direita
    with col1:
        st.title('BI Crome - Sulcromo')
    with col2:
        st.image("Logo_Sulcromo.jpg", use_column_width=True)  # Exibir logotipo com largura da coluna ajustada

    # Obter dados da consulta
    dados = obter_dados()
    # Atualizar a lista de colunas para incluir as novas colunas
    df = pd.DataFrame(dados, columns=[
        'Cliente', 'Tipo Orçamento', 'Peça', 'Rastreabilidade', 'Quantidade', 'Data Recebimento', 
        'Data Inicio OS', 'Data Fim OS', 'Valor Bruto', 'Valor Líquido', 'Responsável Comercial', 
        'Status OS', 'Numero NF', 'Codigo OS', 'Orçamento', 'Data Orçamento', 'Representante', 
        'OC Cliente', 'Situação', 'Setor', 'Tipo Faturamento', 'Data Solicitação', 'Data Carteira',
        'NF Faturamento', 'Data Faturamento', 'NF Devolução', 'Data Devolução', 'Data Oficial Faturamento',
        'Diametro', 'Decimetros', 'Comprimento', 'Camada', 'Exige Certificado', 'Data Inspeção', 'Data Renegociação', 'Motivo Renegociação'  # Novas colunas adicionadas
    ])

    # Criar abas
    aba1, aba2, aba3, aba4, aba5 = st.tabs(["Todos Dados", "Gráficos", "Produção", "Faturamento", "Lead Time"])

    # Chamar a função para exibir a aba 1
    with aba1:
        exibir_aba1(df)

    # Chamar a função para exibir a aba 2
    with aba2:
        exibir_aba2(df)

    # Chamar a função para exibir a aba 3
    with aba3:
        exibir_aba3(df)

    # Chamar a função para exibir a aba 4
    with aba4:
        exibir_aba4(df)
    
    # Chamar a função para exibir a aba 4
    with aba5:
        exibir_aba5(df)

if __name__ == "__main__":
    main()
