# pages/🛍️_Analise_de_Vendas_e_Produtos.py
import streamlit as st
import pandas as pd
import plotly.express as px

# REMOVA a linha st.set_page_config() desta página secundária.
# Ela deve ser definida apenas no seu script principal (Visao_Geral.py).

# Título principal da página
st.title("Análise de Vendas, Produtos e Categorias 🛍️")

# --- Bloco de Verificação e Carregamento dos Dados ---
# Este bloco padrão garante que os dados filtrados existam antes de prosseguir.
if 'df_filtrado' not in st.session_state or st.session_state.df_filtrado.empty:
    st.warning("Não há dados para exibir. Por favor, ajuste os filtros na página principal ou aguarde o carregamento.")
    st.stop()
elif 'data_inicio' in st.session_state and 'data_fim' in st.session_state and st.session_state.data_inicio > st.session_state.data_fim:
     st.error("Data de início não pode ser maior que a data de fim. Ajuste os filtros na sidebar.")
     st.stop()
else:
    df_display = st.session_state.df_filtrado

# --- Abas para organizar a análise ---
tab_geral, tab_categorias, tab_produto_individual = st.tabs([
    "Visão Geral de Produtos", 
    "Análise por Categoria", 
    "Análise Individual de Produto"
])


# --- Aba 1: Visão Geral de Produtos ---
with tab_geral:
    st.header("Desempenho Geral dos Produtos")

    col1, col2 = st.columns(2)
    with col1:
        # Produto Mais Vendido (Quantidade)
        produto_mais_vendido_qtd = df_display.groupby('produto_nome')['quantidade'].sum().idxmax()
        qtd_total = df_display.groupby('produto_nome')['quantidade'].sum().max()
        st.metric("Produto Mais Vendido (em Unidades)", produto_mais_vendido_qtd, f"{qtd_total} Unidades")

    with col2:
        # Produto Mais Rentável (Valor Total)
        produto_mais_rentavel = df_display.groupby('produto_nome')['valor_total'].sum().idxmax()
        valor_total_rentavel = df_display.groupby('produto_nome')['valor_total'].sum().max()
        st.metric("Produto Mais Rentável (em Faturamento)", produto_mais_rentavel, f"R$ {valor_total_rentavel:,.2f}")

    st.markdown("---")
    
    # --- Top N Produtos ---
    col_valor, col_qtd = st.columns(2)
    with col_valor:
        st.subheader("Top 10 Produtos por Faturamento (R$)")
        top_produtos_valor = df_display.groupby('produto_nome')['valor_total'].sum().nlargest(10).sort_values(ascending=True)
        st.bar_chart(top_produtos_valor, horizontal=True)

    with col_qtd:
        st.subheader("Top 10 Produtos por Quantidade Vendida")
        top_produtos_qtd = df_display.groupby('produto_nome')['quantidade'].sum().nlargest(10).sort_values(ascending=True)
        st.bar_chart(top_produtos_qtd, horizontal=True)

    st.info("💡 **Ação:** Foque suas estratégias de marketing nos produtos que geram mais faturamento. Considere criar combos com os produtos mais vendidos em quantidade para aumentar o ticket médio.")


# --- Aba 2: Análise por Categoria ---
with tab_categorias:
    st.header("Desempenho por Categoria")

    col_cat_valor, col_cat_qtd = st.columns(2)
    with col_cat_valor:
        st.subheader("Faturamento por Categoria (R$)")
        faturamento_categoria = df_display.groupby('categoria_nome')['valor_total'].sum().sort_values(ascending=False)
        st.bar_chart(faturamento_categoria)
    
    with col_cat_qtd:
        st.subheader("Itens Vendidos por Categoria")
        itens_categoria = df_display.groupby('categoria_nome')['quantidade'].sum().sort_values(ascending=False)
        st.bar_chart(itens_categoria)

    st.markdown("---")

    # --- Preço Médio e Composição do Faturamento ---
    col_preco_medio, col_pie = st.columns(2)
    with col_preco_medio:
        st.subheader("Preço Médio por Item da Categoria")
        valor_total_cat = df_display.groupby('categoria_nome')['valor_total'].sum()
        qtd_total_cat = df_display.groupby('categoria_nome')['quantidade'].sum()
        preco_medio_cat = (valor_total_cat / qtd_total_cat).fillna(0).sort_values(ascending=False)
        st.dataframe(
            preco_medio_cat.reset_index().rename(columns={'categoria_nome': 'Categoria', 0: 'Preço Médio (R$)'}),
            column_config={"Preço Médio (R$)": st.column_config.NumberColumn(format="R$ %.2f")},
            use_container_width=True,
            hide_index=True
        )

    with col_pie:
        st.subheader("Composição do Faturamento")
        fig = px.pie(
            faturamento_categoria.reset_index(), 
            values='valor_total', 
            names='categoria_nome',
            title='Percentual de Faturamento por Categoria'
        )
        st.plotly_chart(fig, use_container_width=True)

    st.info("💡 **Análise:** Entenda quais categorias são o carro-chefe do seu negócio. Se uma categoria tem um preço médio baixo mas vende muito (como 'Bebidas'), ela é importante para o fluxo de clientes. Se outra tem preço alto (como 'Açaí Especial'), ela é chave para a lucratividade.")


# --- Aba 3: Análise Individual de Produto ---
with tab_produto_individual:
    st.header("Análise Detalhada por Produto")
    st.markdown("Selecione um produto para ver seu desempenho em detalhes.")
    
    # Selecionar um produto
    lista_produtos = sorted(df_display['produto_nome'].unique())
    produto_selecionado = st.selectbox(
        "Selecione um Produto:",
        options=lista_produtos,
        index=0 # Seleciona o primeiro produto por padrão
    )

    if produto_selecionado:
        # Filtrar o DataFrame para apenas o produto selecionado
        df_produto = df_display[df_display['produto_nome'] == produto_selecionado]
        
        st.subheader(f"Desempenho de: {produto_selecionado}")

        # KPIs do produto selecionado
        total_vendido_prod = df_produto['valor_total'].sum()
        qtd_vendida_prod = df_produto['quantidade'].sum()
        preco_medio_prod = total_vendido_prod / qtd_vendida_prod if qtd_vendida_prod > 0 else 0
        
        col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
        col_kpi1.metric("Faturamento Total", f"R$ {total_vendido_prod:,.2f}")
        col_kpi2.metric("Unidades Vendidas", f"{qtd_vendida_prod}")
        col_kpi3.metric("Preço Médio de Venda", f"R$ {preco_medio_prod:,.2f}")

        # Evolução das vendas do produto
        st.markdown("##### Evolução de Vendas no Período")
        vendas_produto_dia = df_produto.groupby(df_produto['data_venda'].dt.date)['valor_total'].sum()
        st.line_chart(vendas_produto_dia, height=300)
        
        # Análise temporal do produto
        col_dia, col_hora = st.columns(2)
        with col_dia:
            st.markdown("##### Vendas por Dia da Semana")
            vendas_prod_dia_semana = df_produto.groupby('dia_semana_venda')['valor_total'].sum()
            dias_ordem = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            nomes_pt = {"Monday": "Segunda", "Tuesday": "Terça", "Wednesday": "Quarta", "Thursday": "Quinta", "Friday": "Sexta", "Saturday": "Sábado", "Sunday": "Domingo"}
            vendas_prod_dia_semana = vendas_prod_dia_semana.reindex(dias_ordem, fill_value=0)
            vendas_prod_dia_semana.index = vendas_prod_dia_semana.index.map(nomes_pt)
            st.bar_chart(vendas_prod_dia_semana)

        with col_hora:
            st.markdown("##### Vendas por Hora do Dia")
            vendas_prod_hora = df_produto.groupby('hora_venda')['valor_total'].sum()
            st.bar_chart(vendas_prod_hora)