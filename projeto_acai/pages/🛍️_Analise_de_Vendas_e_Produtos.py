st.title("Análise de Vendas por Produto e Categoria 🛍️")

if not df_filtrado.empty:
    tab_produtos, tab_categorias = st.tabs(["Análise por Produto", "Análise por Categoria"])

    with tab_produtos:
        st.subheader("Desempenho dos Produtos")
        # Produtos mais vendidos (Top 10 por valor)
        st.markdown("##### Top 10 Produtos Mais Vendidos (por Valor Total)")
        top_produtos_valor = df_filtrado.groupby('produto_nome')['valor_total'].sum().nlargest(10)
        st.dataframe(top_produtos_valor.reset_index().rename(columns={'produto_nome': 'Produto', 'valor_total': 'Valor Total (R$)'}))
        # st.bar_chart(top_produtos_valor) # Outra opção de visualização

        st.markdown("##### Produto Mais Vendido (Quantidade)")
        produto_mais_vendido_qtd = df_filtrado.groupby('produto_nome')['quantidade'].sum().idxmax()
        qtd_produto_mais_vendido = df_filtrado.groupby('produto_nome')['quantidade'].sum().max()
        st.write(f"O produto mais vendido em quantidade é: **{produto_mais_vendido_qtd}** ({qtd_produto_mais_vendido} unidades)")

        st.markdown("##### Produto Mais Lucrativo (Valor Total)")
        produto_mais_lucrativo = df_filtrado.groupby('produto_nome')['valor_total'].sum().idxmax()
        valor_produto_mais_lucrativo = df_filtrado.groupby('produto_nome')['valor_total'].sum().max()
        st.write(f"O produto mais lucrativo (maior valor total de vendas) é: **{produto_mais_lucrativo}** (R$ {valor_produto_mais_lucrativo:,.2f})")

        # Interatividade: clicar em um produto e ver evolução dele
        st.subheader("Evolução de Vendas por Produto Específico")
        produto_selecionado = st.selectbox(
            "Selecione um Produto:",
            options=sorted(df_filtrado['produto_nome'].unique())
        )
        if produto_selecionado:
            df_produto_especifico = df_filtrado[df_filtrado['produto_nome'] == produto_selecionado]
            vendas_produto_dia = df_produto_especifico.groupby(df_produto_especifico['data_venda'].dt.date)['valor_total'].sum()
            st.line_chart(vendas_produto_dia, height=300)


    with tab_categorias:
        st.subheader("Desempenho das Categorias")
        # Categorias mais lucrativas
        st.markdown("##### Categorias Mais Lucrativas (Soma do Valor Total)")
        categorias_lucrativas = df_filtrado.groupby('categoria_nome')['valor_total'].sum().sort_values(ascending=False)
        st.bar_chart(categorias_lucrativas)

        # Gráfico de vendas por categoria e produto (ex: Sunburst ou Treemap com Plotly, ou seleciona categoria e mostra produtos)
        st.markdown("##### Vendas por Produto dentro de uma Categoria")
        categoria_selecionada = st.selectbox(
            "Selecione uma Categoria:",
            options=sorted(df_filtrado['categoria_nome'].unique())
        )
        if categoria_selecionada:
            df_categoria_especifica = df_filtrado[df_filtrado['categoria_nome'] == categoria_selecionada]
            vendas_por_produto_na_categoria = df_categoria_especifica.groupby('produto_nome')['valor_total'].sum().sort_values(ascending=False)
            st.bar_chart(vendas_por_produto_na_categoria, height=300)

        st.markdown("##### Valor Médio por Categoria")
        #  (Soma do valor_total da categoria / número de transações únicas que contêm essa categoria)
        #  Ou (Soma do valor_total da categoria / soma da quantidade de itens da categoria)
        #  Vamos com a primeira interpretação (ticket médio por venda que inclui a categoria):
        #  Ou simplesmente valor total / quantidade de itens:
        valor_total_categoria = df_filtrado.groupby('categoria_nome')['valor_total'].sum()
        quantidade_itens_categoria = df_filtrado.groupby('categoria_nome')['quantidade'].sum()
        valor_medio_item_categoria = (valor_total_categoria / quantidade_itens_categoria).fillna(0)
        st.dataframe(valor_medio_item_categoria.reset_index().rename(columns={'categoria_nome': 'Categoria', 0: 'Preço Médio por Item (R$)'}))

else:
    st.info("Não há dados para exibir com os filtros atuais.")