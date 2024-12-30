import streamlit as st
import pandas as pd
from io import BytesIO

# Função para aplicar os filtros
def filtrar_dados(df, cliente=None, responsaveis=None, situacoes=None, representante=None, tipo_orcamento=None, peca=None, oc_cliente=None, diametro_min=0, diametro_max=0, decimetros_min=0, decimetros_max=0, comprimento_min=0, comprimento_max=0, camada=None):
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
    if diametro_min or diametro_max:
        df['Diametro'] = pd.to_numeric(df['Diametro'], errors='coerce').fillna(0)
        df = df[(df['Diametro'] >= diametro_min) & (df['Diametro'] <= diametro_max)]
    if decimetros_min or decimetros_max:
        df['Decimetros'] = pd.to_numeric(df['Decimetros'], errors='coerce').fillna(0)
        df = df[(df['Decimetros'] >= decimetros_min) & (df['Decimetros'] <= decimetros_max)]
    if comprimento_min or comprimento_max:
        df['Comprimento'] = pd.to_numeric(df['Comprimento'], errors='coerce').fillna(0)
        df = df[(df['Comprimento'] >= comprimento_min) & (df['Comprimento'] <= comprimento_max)]
    if camada:
        df = df[df['Camada'].str.contains(camada, case=False, na=False)]
    return df

# Função para formatar dados para exibição
def formatar_dados_exibicao(df):
    colunas_data = ['Data Recebimento', 'Data Inicio OS', 'Data Fim OS', 'Data Orçamento', 'Data Solicitação', 
                    'Data Carteira', 'Data Faturamento', 'Data Devolução', 'Data Oficial Faturamento', 'Data Inspeção']
    for coluna in colunas_data:
        df[coluna] = pd.to_datetime(df[coluna], errors='coerce').dt.strftime('%d/%m/%Y')
    colunas_valor = ['Valor Bruto', 'Valor Líquido']
    for coluna in colunas_valor:
        df[coluna] = df[coluna].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if pd.notnull(x) and isinstance(x, (int, float)) else x)
    return df

# Função para gerar o arquivo Excel com formatação para valores e datas
def gerar_excel(df):
    # Cria uma cópia do DataFrame para exportação
    df_export = df.copy()
    
    # Converte colunas de valores para numéricas (caso necessário)
    colunas_valores = ['Valor Bruto', 'Valor Líquido']
    for coluna in colunas_valores:
        df_export[coluna] = pd.to_numeric(df_export[coluna], errors='coerce')

    # Converte a coluna "Quantidade" para inteiro
    if 'Quantidade' in df_export.columns:
        df_export['Quantidade'] = pd.to_numeric(df_export['Quantidade'], errors='coerce').fillna(0).astype(int)

    # Converte colunas de data para o formato 'dd/mm/yyyy'
    colunas_data = ['Data Recebimento', 'Data Inicio OS', 'Data Fim OS', 'Data Orçamento', 
                    'Data Solicitação', 'Data Carteira', 'Data Faturamento', 
                    'Data Devolução', 'Data Oficial Faturamento', 'Data Inspeção', 'Data Renegociação']
    for coluna in colunas_data:
        df_export[coluna] = pd.to_datetime(df_export[coluna], errors='coerce').dt.strftime('%d/%m/%Y')

    # Gera o arquivo Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Escreve o DataFrame no arquivo Excel
        df_export.to_excel(writer, index=False, sheet_name='Consulta Carteira')
        worksheet = writer.sheets['Consulta Carteira']
        
        # Configuração de largura automática das colunas
        for idx, col in enumerate(df_export.columns):
            max_len = max(df_export[col].astype(str).map(len).max(), len(col))
            worksheet.set_column(idx, idx, max_len)
    
    output.seek(0)
    return output



# Função para exibir a Aba 1
def exibir_aba1(df):
    st.subheader("Filtros e Resultados")

    col_filtros, col_tabela = st.columns([1, 5])

    with col_filtros:
        st.write("### Filtros")
        
        cliente = st.text_input("Cliente", "", key="cliente_aba1")
        responsaveis = st.multiselect("Responsável Comercial", options=df['Responsável Comercial'].dropna().unique(), key="responsaveis_aba1")
        situacoes = st.multiselect("Situação", options=df['Situação'].dropna().unique(), key="situacoes_aba1")
        representante = st.multiselect("Representante", options=df['Representante'].dropna().unique(), key="representante_aba1")
        tipo_orcamento = st.multiselect("Tipo de Orçamento", options=df['Tipo Orçamento'].dropna().unique(), key="tipo_orcamento_aba1")
        peca = st.text_input("Peça", "", key="peca_aba1")
        oc_cliente = st.text_input("OC Cliente", "", key="oc_cliente_aba1")

        # # Novos filtros com layout "Entre CAMPO AQUI e CAMPO AQUI"
        # st.write("#### Diâmetro")
        # col_diametro_min, col_diametro_max = st.columns(2)
        # with col_diametro_min:
        #     diametro_min = st.number_input("Entre", min_value=0.0, step=0.01, key="diametro_min_aba1")
        # with col_diametro_max:
        #     diametro_max = st.number_input("e", min_value=0.0, step=0.01, key="diametro_max_aba1")

        # st.write("#### Decímetros")
        # col_decimetros_min, col_decimetros_max = st.columns(2)
        # with col_decimetros_min:
        #     decimetros_min = st.number_input("Entre", min_value=0.0, step=0.01, key="decimetros_min_aba1")
        # with col_decimetros_max:
        #     decimetros_max = st.number_input("e", min_value=0.0, step=0.01, key="decimetros_max_aba1")

        # st.write("#### Comprimento")
        # col_comprimento_min, col_comprimento_max = st.columns(2)
        # with col_comprimento_min:
        #     comprimento_min = st.number_input("Entre", min_value=0.0, step=0.01, key="comprimento_min_aba1")
        # with col_comprimento_max:
        #     comprimento_max = st.number_input("e", min_value=0.0, step=0.01, key="comprimento_max_aba1")
        
        # camada = st.text_input("Camada", "", key="camada_aba1")

    with col_tabela:
        # Aplicar os filtros ao DataFrame
        df_filtrado = filtrar_dados(
            df, cliente, responsaveis, situacoes, representante, tipo_orcamento, peca, oc_cliente
            # diametro_min=diametro_min, diametro_max=diametro_max,
            # decimetros_min=decimetros_min, decimetros_max=decimetros_max,
            # comprimento_min=comprimento_min, comprimento_max=comprimento_max,
            # camada=camada
        )

        # Calcular total de valores para os cartões
        total_valor_bruto = df_filtrado['Valor Bruto'].sum()
        total_valor_liquido = df_filtrado['Valor Líquido'].sum()

        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            st.metric('Total Valor Bruto', f'R$ {total_valor_bruto:,.2f}'.replace(",", "X").replace(".", ",").replace("X", "."))
        with col2:
            st.metric('Total Valor Líquido', f'R$ {total_valor_liquido:,.2f}'.replace(",", "X").replace(".", ",").replace("X", "."))
        with col3:
            excel_data = gerar_excel(df_filtrado)
            st.download_button(
                label="Exportar para Excel",
                data=excel_data,
                file_name='consulta_carteira_filtrada.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

        # Formatar e exibir o DataFrame
        df_filtrado_formatado = formatar_dados_exibicao(df_filtrado.copy())
        st.dataframe(df_filtrado_formatado, height=800, use_container_width=True)
