import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Reutilizando as funções de filtro e exibição
from aba1 import filtrar_dados

# Função para formatar os valores monetários no padrão "R$ 1.000,00"
def formatar_valor_brasileiro(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Função para adicionar labels no final das barras, dependendo da orientação
def adicionar_labels(fig, orientation, df):
    if orientation == 'h':
        fig.update_traces(texttemplate=df.apply(lambda x: formatar_valor_brasileiro(x['Valor Líquido']), axis=1), textposition='outside')
        fig.update_layout(yaxis={'autorange': 'reversed'})  # Garantir que os maiores valores fiquem no topo
    else:
        fig.update_traces(texttemplate=df.apply(lambda x: formatar_valor_brasileiro(x['Valor Líquido']), axis=1), textposition='outside')
    return fig

# Função para exibir a Aba 2 com filtros e gráficos dinâmicos
def exibir_aba2(df):
    st.subheader("Filtros e Gráficos")

    # Filtro de Mês/Ano da "Data Oficial Faturamento"
    df['Data Oficial Faturamento'] = pd.to_datetime(df['Data Oficial Faturamento'], errors='coerce')
    df = df.dropna(subset=['Data Oficial Faturamento'])
    meses_disponiveis = df['Data Oficial Faturamento'].dt.to_period('M').unique().strftime('%m/%Y')

    # Filtro padrão para o mês atual e os próximos meses
    mes_atual = datetime.now().strftime('%m/%Y')  # Mês/Ano atual como string
    meses_filtrados = [
        mes for mes in meses_disponiveis if datetime.strptime(mes, '%m/%Y') >= datetime.strptime(mes_atual, '%m/%Y')
    ]
    
    # Elemento de seleção de múltiplos meses
    meses_selecionados = st.multiselect(
        "Mês (Data Oficial Faturamento)",
        options=meses_disponiveis,
        default=meses_filtrados
    )
    
    col_filtros, col_tabela = st.columns([1, 4])  # Layout ajustado: 1 parte filtros, 4 partes gráficos

    with col_filtros:
        st.write("### Filtros")
        
        cliente = st.text_input("Cliente", "", key="cliente_aba2")
        responsaveis = st.multiselect("Responsável Comercial", options=df['Responsável Comercial'].dropna().unique(), key="responsaveis_aba2")
        situacoes = st.multiselect("Situação", options=df['Situação'].dropna().unique(), key="situacoes_aba2")
        representante = st.multiselect("Representante", options=df['Representante'].dropna().unique(), key="representante_aba2")
        tipo_orcamento = st.multiselect("Tipo de Orçamento", options=df['Tipo Orçamento'].dropna().unique(), key="tipo_orcamento_aba2")

    with col_tabela:
        # Aplicar filtros de cliente, responsável, situação, representante e tipo de orçamento
        df_filtrado = filtrar_dados(df, cliente, responsaveis, situacoes, representante, tipo_orcamento)
    
        # Aplicar filtro de mês
        df_filtrado = df_filtrado[df_filtrado['Data Oficial Faturamento'].dt.strftime('%m/%Y').isin(meses_selecionados)]

        # Gráfico 1: Valor Líquido por Tipo de Orçamento
        grafico_tipo_orcamento = df_filtrado.groupby('Tipo Orçamento')['Valor Líquido'].sum().reset_index()
        grafico_tipo_orcamento = grafico_tipo_orcamento.sort_values(by='Valor Líquido', ascending=False)
        fig1 = px.bar(
            grafico_tipo_orcamento, 
            x='Valor Líquido', 
            y='Tipo Orçamento', 
            orientation='h', 
            title="Valor Líquido por Tipo de Orçamento",
            width=None, height=400
        )
        fig1 = adicionar_labels(fig1, 'h', grafico_tipo_orcamento)

        # Gráfico 2: Valor Líquido por Situação
        grafico_situacao = df_filtrado.groupby('Situação')['Valor Líquido'].sum().reset_index()
        grafico_situacao = grafico_situacao.sort_values(by='Valor Líquido', ascending=False)
        fig2 = px.bar(
            grafico_situacao, 
            x='Valor Líquido', 
            y='Situação', 
            orientation='h', 
            title="Valor Líquido por Situação",
            width=None, height=400
        )
        fig2 = adicionar_labels(fig2, 'h', grafico_situacao)

        # Gráfico 3: Valor Líquido por Cliente (Top 10 e barra de rolagem para os demais)
        grafico_cliente = df_filtrado.groupby('Cliente')['Valor Líquido'].sum().reset_index()
        grafico_cliente = grafico_cliente.sort_values(by='Valor Líquido', ascending=False)
        
        # Limitar aos 10 principais e manter o resto para rolagem
        fig3 = px.bar(
            grafico_cliente.head(10),  # Mostra apenas os 10 maiores
            x='Valor Líquido',
            y='Cliente',
            orientation='h',
            title="Valor Líquido por Cliente (Top 10 com barra de rolagem)",
            width=None,
            height=500
        )
        fig3 = adicionar_labels(fig3, 'h', grafico_cliente.head(10))

        fig3.update_layout(
            yaxis=dict(
                tickmode='linear',
                autorange="reversed",
                dtick=1,
                fixedrange=False
            ),
            height=400
        )

        # Gráfico 4: Valor Líquido por Mês/Ano (Data Oficial Faturamento)
        grafico_mes_ano = df_filtrado.groupby(df_filtrado['Data Oficial Faturamento'].dt.to_period('M'))['Valor Líquido'].sum().reset_index()
        grafico_mes_ano['Data Oficial Faturamento'] = grafico_mes_ano['Data Oficial Faturamento'].dt.strftime('%m/%Y')
        fig4 = px.bar(
            grafico_mes_ano, 
            x='Data Oficial Faturamento', 
            y='Valor Líquido', 
            title="Valor Líquido por Mês/Ano (Data Oficial Faturamento)",
            labels={'Data Oficial Faturamento': 'Mês/Ano'},
            width=None, height=400
        )
        fig4 = adicionar_labels(fig4, 'v', grafico_mes_ano)

        # Exibir gráficos em uma grade 2x2 com keys únicos
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig1, use_container_width=True, key="grafico_tipo_orcamento")
            st.plotly_chart(fig3, use_container_width=True, key="grafico_cliente_top10")
        with col2:
            st.plotly_chart(fig2, use_container_width=True, key="grafico_situacao")
            st.plotly_chart(fig4, use_container_width=True, key="grafico_mes_ano")
