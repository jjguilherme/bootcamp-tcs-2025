# Em cada página ou no script principal se for gerenciado centralmente
import streamlit as st
import pandas as pd
import app_utils
from datetime import datetime, timedelta

st.set_page_config(layout="wide", page_title="Dashboard Açaí - Visao Geral")

st.sidebar.header("Filtros 🎛️")
formas_pagamento_opcoes, clientes_opcoes, min_data_bd, max_data_bd = app_utils.obter_opcoes_filtro()

data_inicio = st.sidebar.date_input("Data Início", min_data_bd, min_value=min_data_bd, max_value=max_data_bd)
data_fim = st.sidebar.date_input("Data Fim", max_data_bd, min_value=min_data_bd, max_value=max_data_bd)

if data_inicio > data_fim:
    st.sidebar.error("Data de início não pode ser maior que a data de fim.")
    st.stop() 

formas_pagamento_selecionadas = st.sidebar.multiselect(
    "Forma de Pagamento",
    options=formas_pagamento_opcoes,
    default=[] # Pode deixar vazio ou pré-selecionar algumas
)
clientes_selecionados = st.sidebar.multiselect(
    "Cliente",
    options=clientes_opcoes,
    default=[]
)

# Carregar dados com base nos filtros
df_filtrado = app_utils.carregar_dados_base(data_inicio, data_fim, formas_pagamento_selecionadas, clientes_selecionados)

# Adicionar colunas úteis de data/hora se df_filtrado não estiver vazio
if not df_filtrado.empty:
    df_filtrado['hora_venda'] = df_filtrado['data_venda'].dt.hour
    df_filtrado['dia_semana_venda'] = df_filtrado['data_venda'].dt.day_name()
    df_filtrado['mes_ano_venda'] = df_filtrado['data_venda'].dt.to_period('M').astype(str) # Para agrupar por mês/ano
    
    st.session_state.df_filtrado = df_filtrado 
else:
    st.warning("Nenhum dado encontrado para os filtros selecionados.")
    # st.stop() # Opcional: parar se não houver dados, ou permitir que a página exiba "sem dados"

st.title("Painel de Vendas Açaí - Visão Geral 📈")

if not df_filtrado.empty:
    # --- KPIs ---
    st.subheader("Indicadores Chave 📊")
    total_vendas_valor = df_filtrado['valor_total'].sum()
    num_transacoes = df_filtrado['venda_id'].nunique() # Assumindo que venda_id é único por transação
    ticket_medio = total_vendas_valor / num_transacoes if num_transacoes > 0 else 0
    quantidade_vendida = df_filtrado['quantidade'].sum()
    clientes_unicos = df_filtrado['cliente'].nunique()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Vendas", f"R$ {total_vendas_valor:,.2f}")
    col2.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}")
    col3.metric("Itens Vendidos", f"{quantidade_vendida:,}")
    # st.metric("Clientes Únicos", f"{clientes_unicos}") # Pode ser um KPI aqui ou na página de clientes

    # --- Evolução das Vendas ---
    st.subheader("Evolução das Vendas no Período 📅")
    # Agrupar por dia para o gráfico de evolução
    vendas_por_dia = df_filtrado.groupby(df_filtrado['data_venda'].dt.date)['valor_total'].sum()
    st.line_chart(vendas_por_dia)

    # --- Quick Insights (Top Produtos/Categorias) ---
    st.subheader("Destaques Rápidos 🏆")
    col_prod, col_cat = st.columns(2)

    with col_prod:
        st.markdown("#### Top 5 Produtos (por Quantidade)")
        top_produtos_qtd = df_filtrado.groupby('produto_nome')['quantidade'].sum().nlargest(5)
        st.bar_chart(top_produtos_qtd)

    with col_cat:
        st.markdown("#### Top 3 Categorias (por Lucratividade)") # Lucratividade = valor_total
        top_categorias_valor = df_filtrado.groupby('categoria_nome')['valor_total'].sum().nlargest(3)
        st.bar_chart(top_categorias_valor)
else:
    st.info("Não há dados para exibir com os filtros atuais.")