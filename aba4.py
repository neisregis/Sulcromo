import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

# Função para gerar o arquivo Excel a partir do dataframe
def gerar_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Faturamento')
        for column in df:
            col_idx = df.columns.get_loc(column)
            writer.sheets['Faturamento'].set_column(col_idx, col_idx, max(df[column].astype(str).map(len).max(), len(column)))
    output.seek(0)
    return output

# Função para exibir a Aba 4 - Faturamento
def exibir_aba4(df):
    st.subheader("Faturamento")

    # Filtrar dados para situação "FATURADO"
    df_faturado = df[df['Situação'] == "FATURADO"].copy()

    # Extrair os meses/anos únicos da coluna "Data Oficial Faturamento"
    df_faturado['Data Oficial Faturamento'] = pd.to_datetime(df_faturado['Data Oficial Faturamento'], errors='coerce')
    df_faturado = df_faturado.dropna(subset=['Data Oficial Faturamento'])  # Remover linhas sem data
    meses_disponiveis = sorted(df_faturado['Data Oficial Faturamento'].dt.to_period('M').unique(), key=lambda x: x.start_time)

    # Definir mês/ano selecionado padrão
    if "selected_month" not in st.session_state:
        st.session_state.selected_month = meses_disponiveis[-1]  # Define o mês mais recente como padrão

    # Exibir os botões de meses/anos como "cards" clicáveis
    st.write("### Filtro por Mês/Ano")
    col_buttons = st.columns(len(meses_disponiveis))
    for i, mes in enumerate(meses_disponiveis):
        mes_label = mes.strftime('%m/%Y')
        if col_buttons[i].button(mes_label):
            st.session_state.selected_month = mes  # Atualizar o mês selecionado no estado da sessão

    # Aplicar o filtro de mês com base no estado da sessão
    selected_month = st.session_state.selected_month
    df_faturado = df_faturado[df_faturado['Data Oficial Faturamento'].dt.to_period('M') == selected_month]

    # Layout com filtros à esquerda e cards + tabela na parte superior direita
    col_filtros, col_conteudo = st.columns([1, 5])

    # Adicionar filtros adicionais
    with col_filtros:
        st.write("### Filtros")
        cliente = st.text_input("Cliente")
        responsaveis = st.multiselect("Responsável Comercial", options=df_faturado['Responsável Comercial'].dropna().unique())
        tipo_orcamento = st.multiselect("Tipo de Orçamento", options=df_faturado['Tipo Orçamento'].dropna().unique())
        representante = st.multiselect("Representante", options=df_faturado['Representante'].dropna().unique())

        # Aplicar filtros adicionais
        if cliente:
            df_faturado = df_faturado[df_faturado['Cliente'].str.contains(cliente, case=False, na=False)]
        if responsaveis:
            df_faturado = df_faturado[df_faturado['Responsável Comercial'].isin(responsaveis)]
        if tipo_orcamento:
            df_faturado = df_faturado[df_faturado['Tipo Orçamento'].isin(tipo_orcamento)]
        if representante:
            df_faturado = df_faturado[df_faturado['Representante'].isin(representante)]

    # Calcular os valores para os cartões
    total_valor_liquido = df_faturado['Valor Líquido'].sum()
    total_pecas_faturadas = df_faturado['Quantidade'].fillna(0).astype(int).sum()
    total_clientes_distintos = df_faturado['Cliente'].nunique()
    total_os = len(df_faturado)  # Total de registros, contando cada linha

    # Calcular a quantidade de OS em dia e atrasadas, sem usar `.nunique()`
    df_faturado['Data Fim'] = pd.to_datetime(df_faturado['Data Fim OS'], errors='coerce')
    df_faturado['Diferença Dias'] = (df_faturado['Data Oficial Faturamento'] - df_faturado['Data Fim']).dt.days.fillna(0).astype(int)

    os_em_dia = df_faturado[(df_faturado['Diferença Dias'] <= 0) | (df_faturado['Data Fim'].isna())].shape[0]
    os_atrasadas = df_faturado[df_faturado['Diferença Dias'] > 0].shape[0]

    # Exibir os cartões com as métricas no lado direito, acima da tabela
    with col_conteudo:
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            st.metric("Total Valor Líquido", f"R$ {total_valor_liquido:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        with col2:
            st.metric("Peças Faturadas", total_pecas_faturadas)
        with col3:
            st.metric("Clientes Faturados", total_clientes_distintos)
        with col4:
            st.metric("Total de OS", total_os)
        with col5:
            st.metric("OS em Dia", os_em_dia)
        with col6:
            st.metric("OS Atrasadas", os_atrasadas)

        # Preparar dados para exibição na tabela
        df_faturado['Data Oficial Faturamento Formatada'] = df_faturado['Data Oficial Faturamento'].dt.strftime('%d/%m/%Y')
        df_faturado['Data Fim Formatada'] = df_faturado['Data Fim'].dt.strftime('%d/%m/%Y')
        df_faturado['Quantidade'] = df_faturado['Quantidade'].fillna(0).astype(int)

        # Exibir a tabela com os dados
        df_tabela = df_faturado[['Codigo OS', 'Cliente', 'Peça', 'Quantidade', 'Data Fim Formatada', 'Data Oficial Faturamento Formatada', 'Diferença Dias']]
        st.dataframe(df_tabela, use_container_width=True)

        # Botão para exportar a tabela em Excel
        excel_data = gerar_excel(df_tabela)
        st.download_button(
            label="Exportar para Excel",
            data=excel_data,
            file_name='faturamento.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

# Exemplo de chamada da função no script principal
# exibir_aba4(df)
