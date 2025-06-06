# pages/💳_Analise_de_Pagamentos.py
import streamlit as st
import pandas as pd

# Define o layout da página e o título que aparece na aba do navegador
#st.set_page_config(layout="wide", page_title="Análise de Pagamentos")

# Título principal da página
st.title("Análise por Forma de Pagamento 💳")

# --- Bloco de Verificação e Carregamento dos Dados ---
# Este bloco padrão garante que os dados filtrados existam antes de prosseguir.
# Ele lê os dados que foram carregados e processados no script principal (Visao_Geral.py).
if 'df_filtrado' not in st.session_state or st.session_state.df_filtrado.empty:
    st.warning("Não há dados para exibir. Por favor, ajuste os filtros na página principal ou aguarde o carregamento.")
    st.stop()
elif 'data_inicio' in st.session_state and 'data_fim' in st.session_state and st.session_state.data_inicio > st.session_state.data_fim:
     st.error("Data de início não pode ser maior que a data de fim. Ajuste os filtros na sidebar.")
     st.stop()
else:
    df_display = st.session_state.df_filtrado

# --- Cálculos Principais ---
# É uma boa prática fazer os cálculos uma vez no início e reutilizar os resultados.
vendas_por_fp_valor = df_display.groupby('forma_pagamento_nome')['valor_total'].sum()
transacoes_por_fp = df_display.groupby('forma_pagamento_nome')['venda_id'].nunique()
ticket_medio_fp = (vendas_por_fp_valor / transacoes_por_fp).fillna(0)


# --- KPI (Indicador Chave) em Destaque ---
st.subheader("Destaque Principal")
if not transacoes_por_fp.empty:
    # Identifica a forma de pagamento com o maior número de transações
    fp_mais_usada = transacoes_por_fp.idxmax()
    st.metric("Forma de Pagamento Mais Popular", fp_mais_usada)
else:
    st.metric("Forma de Pagamento Mais Popular", "N/A")


# --- Análise Comparativa: Volume vs. Valor ---
st.subheader("Comparativo de Formas de Pagamento")
st.markdown("Entenda como cada forma de pagamento contribui em valor total (R$) e em número de transações.")

# Organizar os gráficos lado a lado para facilitar a comparação
col_valor, col_volume = st.columns(2)

with col_valor:
    st.markdown("##### Valor Total por Forma de Pagamento (R$)")
    if not vendas_por_fp_valor.empty:
        st.bar_chart(vendas_por_fp_valor.sort_values(ascending=False))
    else:
        st.write("Sem dados de valor para exibir.")

with col_volume:
    st.markdown("##### Número de Transações por Forma de Pagamento")
    if not transacoes_por_fp.empty:
        st.bar_chart(transacoes_por_fp.sort_values(ascending=False))
    else:
        st.write("Sem dados de transações para exibir.")

# Fornecer um insight acionável para o comerciante
st.info("""
    💡 **Análise:** Compare os dois gráficos.
    - Uma forma de pagamento pode ter **muitas transações (alto volume)** mas um **valor total baixo**, indicando uso para compras pequenas (ex: dinheiro para um item).
    - Outra pode ter **poucas transações (baixo volume)** mas um **valor total alto**, indicando uso para compras maiores (ex: cartão de crédito para levar para a família toda).
""")


# --- Análise de Ticket Médio ---
st.subheader("Ticket Médio por Forma de Pagamento 💵")
st.markdown("Veja o valor médio que os clientes gastam em uma transação com cada método.")

if not ticket_medio_fp.empty:
    st.bar_chart(ticket_medio_fp.sort_values(ascending=False))

    # --- Tabela Detalhada para dados precisos ---
    st.markdown("##### Dados Detalhados")
    df_pagamentos_summary = pd.DataFrame({
        'Valor Total (R$)': vendas_por_fp_valor,
        'Nº de Transações': transacoes_por_fp,
        'Ticket Médio (R$)': ticket_medio_fp
    }).reset_index().rename(columns={'forma_pagamento_nome': 'Forma de Pagamento'})
    
    # Ordenar pela coluna desejada, por exemplo, por Valor Total
    df_pagamentos_summary = df_pagamentos_summary.sort_values('Valor Total (R$)', ascending=False)
    
    # Usar column_config para formatar os números como moeda, melhorando a leitura
    st.dataframe(
        df_pagamentos_summary,
        column_config={
            "Valor Total (R$)": st.column_config.NumberColumn(format="R$ %.2f"),
            "Ticket Médio (R$)": st.column_config.NumberColumn(format="R$ %.2f"),
        },
        use_container_width=True,
        hide_index=True
    )
else:
    st.write("Não foi possível calcular o ticket médio.")

st.info("""
    💡 **Ação:** Formas de pagamento com **ticket médio alto** (ex: Cartão de Crédito) podem ser um bom canal para incentivar compras maiores, talvez com opções de parcelamento. Já formas com **ticket médio baixo** (ex: Dinheiro ou Pix) são importantes para garantir troco e agilidade no caixa para compras rápidas.
""")