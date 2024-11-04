import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

# Função para gerar o arquivo Excel a partir do dataframe
def gerar_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Produção')
        for column in df:
            col_idx = df.columns.get_loc(column)
            writer.sheets['Produção'].set_column(col_idx, col_idx, max(df[column].astype(str).map(len).max(), len(column)))
    output.seek(0)
    return output

# Função para exibir a Aba 3
def exibir_aba3(df):
    st.subheader("Produção - OS's em Aberto")

    # Filtrar dados para situação "EM PRODUÇÃO"
    df_producao = df[df['Situação'] == "EM PRODUÇÃO"].copy()  # Evitar SettingWithCopyWarning

    # Layout com filtros à esquerda e cards + tabela na parte superior direita
    col_filtros, col_conteudo = st.columns([1, 5])

    with col_filtros:
        st.write("### Filtros")
        
        # Adicionar Filtros adicionais
        cliente = st.text_input("Cliente", key="cliente_aba3")
        responsaveis = st.multiselect("Responsável Comercial", options=df_producao['Responsável Comercial'].dropna().unique(), key="responsaveis_aba3")
        tipo_orcamento = st.multiselect("Tipo de Orçamento", options=df_producao['Tipo Orçamento'].dropna().unique(), key="tipo_orcamento_aba3")
        data_fim = st.date_input("Data Fim", key="data_fim_aba3")

        # Aplicar filtros conforme os valores selecionados
        if cliente:
            df_producao = df_producao[df_producao['Cliente'].str.contains(cliente, case=False, na=False)]
        if responsaveis:
            df_producao = df_producao[df_producao['Responsável Comercial'].isin(responsaveis)]
        if tipo_orcamento:
            df_producao = df_producao[df_producao['Tipo Orçamento'].isin(tipo_orcamento)]
        if data_fim:
            data_fim = pd.Timestamp(data_fim)
            df_producao['Data Fim OS'] = pd.to_datetime(df_producao['Data Fim OS'], errors='coerce')
            df_producao = df_producao[(df_producao['Data Fim OS'].notna()) & (df_producao['Data Fim OS'] <= data_fim)]

    # Selecionar apenas as colunas desejadas
    df_producao = df_producao[['Codigo OS', 'Cliente', 'Peça', 'Quantidade', 'Data Fim OS', 'Data Recebimento', 'Orçamento', 'Numero NF']]
    df_producao['Quantidade'] = df_producao['Quantidade'].fillna(0).astype(int)

    # Ordenar pela coluna "Data Fim OS", trazendo NaT (sem data) por último
    df_producao['Data Fim OS'] = pd.to_datetime(df_producao['Data Fim OS'], errors='coerce')
    df_producao = df_producao.sort_values(by=['Data Fim OS'], na_position='last')

    # Criar uma coluna formatada para exibição e manter "Data Fim OS" como Timestamp para ordenação e estilização
    df_producao['Data Fim Formatada'] = df_producao['Data Fim OS'].dt.strftime('%d/%m/%Y')
    df_producao['Data Recebimento'] = pd.to_datetime(df_producao['Data Recebimento'], errors='coerce', dayfirst=True).dt.strftime('%d/%m/%Y')

    # Contagem de linhas e soma de peças
    total_linhas = len(df_producao)
    total_pecas = df_producao['Quantidade'].sum()

    # Exibir contagem de linhas e peças como métricas e botão de exportação
    with col_conteudo:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.metric("Total de Registros", total_linhas)
        with col2:
            st.metric("Total de Peças", total_pecas)
        with col3:
            excel_data = gerar_excel(df_producao)
            st.download_button(
                label="Exportar para Excel",
                data=excel_data,
                file_name='producao.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

        # Definir a cor da célula para valores da coluna "Data Fim OS" menores que hoje
        hoje = datetime.now().date()
        
        def aplicar_estilos(val):
            val_date = pd.to_datetime(val, errors='coerce', dayfirst=True)
            return 'background-color: red' if pd.notnull(val_date) and val_date.date() < hoje else ''

        # Exibir tabela com a coluna formatada para exibição e aplicar estilos
        df_producao_display = df_producao[['Codigo OS', 'Cliente', 'Peça', 'Quantidade', 'Data Fim Formatada', 'Data Recebimento', 'Orçamento', 'Numero NF']]
        st.dataframe(
            df_producao_display.style.map(aplicar_estilos, subset=['Data Fim Formatada']),
            height=800,  # Ajuste para mostrar 30 linhas
            use_container_width=True
        )
