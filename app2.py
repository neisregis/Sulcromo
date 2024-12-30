import mysql.connector
from flask import Flask, render_template, request, send_file
import pandas as pd
from io import BytesIO

app = Flask(__name__)

# Função para configurar a conexão com o banco de dados
from config import config  # Certifique-se de que o arquivo config.py está configurado corretamente

# Função para aplicar filtros
def filtrar_dados(df, cliente=None, responsaveis=None, situacoes=None, representante=None, tipo_orcamento=None, peca=None, oc_cliente=None):
    if cliente:
        df = df[df['Cliente'].str.contains(cliente, case=False, na=False)]
    if responsaveis:
        df = df[df['Responsável Comercial'].isin(responsaveis)]
    if situacoes:
        df = df[df['Situação'].isin(situacoes)]
    if representante:
        df = df[df['Representante'].isin(representante)]
    if tipo_orcamento:
        df = df[df['Tipo Orçamento'].isin(tipo_orcamento)]
    if peca:
        df = df[df['Peça'].str.contains(peca, case=False, na=False)]
    if oc_cliente:
        df = df[df['OC Cliente'].str.contains(oc_cliente, case=False, na=False)]
    return df

# Função para obter dados a partir do banco de dados
def obter_dados():
    try:
        conexao = mysql.connector.connect(**config())  # Passa os parâmetros do dicionário corretamente
        cursor = conexao.cursor()
        
        # Nova consulta SQL com as colunas renomeadas
        query = """
        SELECT 
            CLIENTE as 'Cliente',
            TIPO_ORCAMENTO as 'Tipo Orçamento', 
            PECA as 'Peça', 
            RASTR as 'Rastreabilidade', 
            QUANTIDADE as 'Quantidade', 
            DATA_RECEBIMENTO_NF as 'Data Recebimento', 
            DATA_INICIO_OS as 'Data Inicio OS', 
            DATA_FIM_OS as 'Data Fim OS', 
            VALOR_BRUTO as 'Valor Bruto', 
            VALOR_LIQUIDO as 'Valor Líquido', 
            RESPONSAVEL_COMERCIAL as 'Responsável Comercial', 
            STATUS_OS as 'Status OS', 
            NUMERO_NF as 'Numero NF', 
            CODIGO_OS as 'Codigo OS', 
            ORCAMENTO as 'Orçamento', 
            DATA_PROPOSTA as 'Data Orçamento', 
            REPRESENTANTE as 'Representante', 
            OC_CLIENTE as 'OC Cliente', 
            SITUACAO as 'Situação', 
            SETOR as 'Setor', 
            TIPO_FATURAMENTO as 'Tipo Faturamento',
            DATA_SOLICITACAO as 'Data Solicitação', 
            DATA_CARTEIRA as 'Data Carteira', 
            NF_FATURAMENTO as 'NF Faturamento', 
            DATA_FATURAMENTO as 'Data Faturamento', 
            NF_DEVOLUCAO as 'NF Devolução', 
            DATA_DEVOLUCAO as 'Data Devolução', 
            DATA_OFICIAL_FATURAMENTO as 'Data Oficial Faturamento', 
            DIAMETRO as 'Diametro', 
            COMPRIMENTO as 'Comprimento', 
            DECIMETROS as 'Decimetros', 
            CAMADA as 'Camada', 
            EXIGE_CERTIFICADO as 'Exige Certificado', 
            DATA_INSPECAO as 'Data Inspeção',
            DATA_RENEGOCIACAO as 'Data Renegociação',
            MOTIVO_RENEGOCIACAO as 'Motivo Renegociação'
        FROM sulcromo_db.VW_CONSULTA_GERAL;
        """
        
        # Executar a consulta
        cursor.execute(query)
        resultados = cursor.fetchall()
        
        # Obter os nomes das colunas da consulta
        colunas = [desc[0] for desc in cursor.description]
        
        # Fechar a conexão
        cursor.close()
        conexao.close()
        
        # Retornar os dados como um DataFrame do pandas
        return pd.DataFrame(resultados, columns=colunas)
    except Exception as e:
        print(f"Erro ao obter dados: {e}")
        return pd.DataFrame()  # Retorna um DataFrame vazio em caso de erro
    
# Função para formatar dados para exibição
def formatar_dados_exibicao(df):
    colunas_data = [
        'Data Recebimento', 'Data Inicio OS', 'Data Fim OS', 'Data Orçamento', 
        'Data Solicitação', 'Data Carteira', 'Data Faturamento', 
        'Data Devolução', 'Data Oficial Faturamento', 'Data Inspeção', 'Data Renegociação'
    ]
    for coluna in colunas_data:
        if coluna in df.columns:
            df[coluna] = pd.to_datetime(df[coluna], errors='coerce').dt.strftime('%d/%m/%Y')
    
    colunas_valor = ['Valor Bruto', 'Valor Líquido']
    for coluna in colunas_valor:
        if coluna in df.columns:
            df[coluna] = df[coluna].apply(
                lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") 
                if pd.notnull(x) and isinstance(x, (int, float)) else x
            )
    return df

@app.route('/', methods=['GET', 'POST'])
def index():
    # Obter os dados do banco
    df = obter_dados()
    
    # Verificar se os dados foram carregados corretamente
    if df.empty:
        return "Erro ao carregar dados ou tabela vazia no banco de dados.", 500

    # Obter filtros do formulário
    if request.method == 'POST':
        filtros = {
            'cliente': request.form.get('cliente'),
            'responsaveis': request.form.getlist('responsaveis'),  # Para múltiplos valores
            'situacoes': request.form.getlist('situacoes'),        # Para múltiplos valores
            'representante': request.form.getlist('representante'),# Para múltiplos valores
            'tipo_orcamento': request.form.getlist('tipo_orcamento'), # Para múltiplos valores
            'peca': request.form.get('peca'),
            'oc_cliente': request.form.get('oc_cliente')
        }
    else:
        filtros = {
            'cliente': None,
            'responsaveis': [],
            'situacoes': [],
            'representante': [],
            'tipo_orcamento': [],
            'peca': None,
            'oc_cliente': None
        }

    # Aplicar filtros
    df_filtrado = filtrar_dados(
        df,
        cliente=filtros['cliente'],
        responsaveis=filtros['responsaveis'],
        situacoes=filtros['situacoes'],
        representante=filtros['representante'],
        tipo_orcamento=filtros['tipo_orcamento'],
        peca=filtros['peca'],
        oc_cliente=filtros['oc_cliente']
    )

    # Calcular métricas para exibição nos cartões
    total_valor_bruto = df_filtrado['Valor Bruto'].sum()
    total_valor_liquido = df_filtrado['Valor Líquido'].sum()

    # Formatar os dados para exibição na tabela
    df_formatado = formatar_dados_exibicao(df_filtrado.copy())

    # Renderizar o HTML com os dados formatados
    return render_template(
        'index.html',
        df=df_formatado,
        total_valor_bruto=f"R$ {total_valor_bruto:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        total_valor_liquido=f"R$ {total_valor_liquido:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        filtros=filtros,
        responsaveis=df['Responsável Comercial'].dropna().unique(),
        situacoes=df['Situação'].dropna().unique(),
        representantes=df['Representante'].dropna().unique(),
        tipos_orcamento=df['Tipo Orçamento'].dropna().unique()
    )


if __name__ == '__main__':
    app.run(debug=True)
