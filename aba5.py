import locale  # Para definir a localização dos meses em português
from datetime import datetime
import pandas as pd
import streamlit as st
from io import BytesIO

# Configurar a localização para português
locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')  # Para sistemas baseados em Unix
# locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')  # Para Windows

def exibir_aba5(df):
    st.subheader("Lead Time")

    # Filtrar apenas registros com situação "FATURADO"
    df = df[df['Situação'] == "FATURADO"].copy()

    # Conversão de colunas de datas para datetime
    df['Data Recebimento'] = pd.to_datetime(df['Data Recebimento'], errors='coerce')
    df['Data Inspeção'] = pd.to_datetime(df['Data Inspeção'], errors='coerce')
    df['Data Inicio OS'] = pd.to_datetime(df['Data Inicio OS'], errors='coerce')
    df['Data Fim OS'] = pd.to_datetime(df['Data Fim OS'], errors='coerce')
    df['Data Renegociação'] = pd.to_datetime(df['Data Renegociação'], errors='coerce')
    df['Data Faturamento'] = pd.to_datetime(df['Data Faturamento'], errors='coerce')

    # Cálculo dos lead times
    df['Em Atraso / Em Dia'] = (df['Data Fim OS'] - df['Data Faturamento']).dt.days
    df['Prazo de Entrega (Total)'] = (df['Data Faturamento'] - df['Data Recebimento']).dt.days
    df['Prazo Inspeção'] = (df['Data Inspeção'] - df['Data Recebimento']).dt.days

    # Criação do filtro de mês/ano
    df['Mês/Ano Faturamento'] = df['Data Faturamento'].dt.strftime('%b/%y')  # Exemplo: jan/24
    df['Mês/Ano Faturamento'] = df['Mês/Ano Faturamento'].fillna('')  # Substituir valores nulos por strings vazias
    df['Mês/Ano Faturamento'] = df['Mês/Ano Faturamento'].map(
        lambda x: x.capitalize() if x else x  # Ajustar capitalização, ignorando strings vazias
    )

    # Meses disponíveis no filtro
    meses_disponiveis = sorted(
        [mes for mes in df['Mês/Ano Faturamento'].unique() if mes],  # Filtrar valores válidos
        key=lambda x: datetime.strptime(x, '%b/%y')
    )

    # Obter o mês atual no formato apropriado
    mes_atual = datetime.now().strftime('%b/%y').capitalize()

    # Layout com filtros à esquerda e tabela de resultados na direita
    st.write("### Indicadores")

    # Aplicar filtros
    col_filtros, col_conteudo = st.columns([1, 5])

    with col_filtros:
        st.write("### Filtros")

        # Filtro de mês/ano com múltipla escolha
        meses_selecionados = st.multiselect(
            "Selecione os meses/anos:",
            options=meses_disponiveis,
            default=[mes_atual],  # Selecionar o mês atual por padrão
            key="mes_ano_faturamento_aba5"
        )

        cliente = st.text_input("Cliente", key="cliente_aba5")
        responsaveis = st.multiselect("Responsável Comercial", options=df['Responsável Comercial'].dropna().unique(), key="responsaveis_aba5")
        representante = st.multiselect("Representante", options=df['Representante'].dropna().unique(), key="representante_aba5")

        # Aplicar filtros
        df_filtrado = df.copy()
        if meses_selecionados:
            df_filtrado = df_filtrado[df_filtrado['Mês/Ano Faturamento'].isin(meses_selecionados)]
        if cliente:
            df_filtrado = df_filtrado[df_filtrado['Cliente'].str.contains(cliente, case=False, na=False)]
        if responsaveis:
            df_filtrado = df_filtrado[df_filtrado['Responsável Comercial'].isin(responsaveis)]
        if representante:
            df_filtrado = df_filtrado[df_filtrado['Representante'].isin(representante)]

    # Atualizar os valores para os cards com o DataFrame filtrado
    faturamentos = len(df_filtrado)  # Número total de registros filtrados
    media_atraso = df_filtrado['Em Atraso / Em Dia'].mean()  # Média de atraso/em dia
    faturamentos_atrasados = len(df_filtrado[df_filtrado['Em Atraso / Em Dia'] < 0])  # Soma de registros com atraso
    percentual_em_dia = len(df_filtrado[df_filtrado['Em Atraso / Em Dia'] >= 0]) / faturamentos * 100 if faturamentos > 0 else 0  # % em dia
    media_prazo_total = df_filtrado['Prazo de Entrega (Total)'].mean()  # Média do prazo total

    # Exibir os cards logo abaixo do título
    st.write("### Indicadores")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(label="Faturamentos", value=f"{faturamentos}")

    with col2:
        st.metric(label="Média de Atraso / Em Dia", value=f"{media_atraso:.1f} dias")

    with col3:
        st.metric(label="Faturamentos Atrasados", value=f"{faturamentos_atrasados}")

    with col4:
        st.metric(label="% Faturamentos em Dia", value=f"{percentual_em_dia:.1f}%")

    with col5:
        st.metric(label="Média de Prazo Total", value=f"{media_prazo_total:.1f} dias")

    # Preparar dados para exibição na tabela
    df_tabela = df_filtrado[[
        'Cliente', 'Representante', 'Responsável Comercial', 'Codigo OS', 
        'Data Recebimento', 'Data Inspeção', 'Data Inicio OS', 'Data Fim OS', 'Data Renegociação',
        'Data Faturamento', 'Em Atraso / Em Dia', 'Prazo de Entrega (Total)', 'Prazo Inspeção'
    ]]

    # Formatar datas para exibição
    for coluna in ['Data Recebimento', 'Data Inspeção', 'Data Inicio OS', 'Data Fim OS', 'Data Renegociação', 'Data Faturamento']:
        df_tabela[coluna] = df_tabela[coluna].dt.strftime('%d/%m/%Y')

    # Exibir a tabela
    with col_conteudo:
        st.write("### Resultados")
        st.dataframe(df_tabela, use_container_width=True)

        # Botão para exportar a tabela em Excel
        excel_data = gerar_excel(df_tabela)
        st.download_button(
            label="Exportar para Excel",
            data=excel_data,
            file_name='lead_time.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

# Função para gerar o arquivo Excel a partir do dataframe
def gerar_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Lead Time')
        for column in df:
            col_idx = df.columns.get_loc(column)
            writer.sheets['Lead Time'].set_column(col_idx, col_idx, max(df[column].astype(str).map(len).max(), len(column)))
    output.seek(0)
    return output
