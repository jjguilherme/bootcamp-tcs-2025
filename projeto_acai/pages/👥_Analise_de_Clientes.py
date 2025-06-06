# pages/👥_Analise_de_Clientes.py
import streamlit as st
import pandas as pd

#st.set_page_config(layout="wide", page_title="Análise de Clientes")

st.title("Análise de Clientes 👥")

# --- Verificação e Carregamento dos Dados ---
# Acessa o DataFrame filtrado que foi carregado e processado no script principal
if 'df_filtrado' not in st.session_state or st.session_state.df_filtrado.empty:
    st.warning("Não há dados para exibir. Por favor, ajuste os filtros na página principal ou aguarde o carregamento.")
    st.stop()

# Checa se houve erro de data nos filtros (definido no script principal)
if 'data_inicio' in st.session_state and 'data_fim' in st.session_state and st.session_state.data_inicio > st.session_state.data_fim:
     st.error("Data de início não pode ser maior que a data de fim. Ajuste os filtros na sidebar.")
     st.stop()
else:
    df_display = st.session_state.df_filtrado


# --- KPI Principal da Página ---
st.subheader("Visão Geral dos Clientes")
clientes_unicos = df_display['cliente'].nunique()
st.metric("Total de Clientes Únicos no Período", f"{clientes_unicos}")
st.info(f"Um total de **{clientes_unicos} clientes diferentes** fizeram compras no período, com os filtros selecionados.")


# --- Análise de Top Clientes ---
st.subheader("Ranking de Clientes 🏆")
st.markdown("Identifique seus clientes mais importantes por valor gasto e por frequência de visitas.")

tab_valor, tab_frequencia = st.tabs(["Top Clientes por Valor Gasto", "Top Clientes por Frequência"])

with tab_valor:
    st.markdown("##### Clientes que mais gastaram (R$)")
    top_clientes_valor = df_display.groupby('cliente')['valor_total'].sum().nlargest(10).sort_values(ascending=True)
    
    if not top_clientes_valor.empty:
        st.bar_chart(top_clientes_valor, horizontal=True)
        st.info("💡 **Ação:** Considere criar um programa de fidelidade ou oferecer um desconto especial para esses clientes como agradecimento.")
    else:
        st.write("Não há dados de valor gasto para exibir.")

with tab_frequencia:
    st.markdown("##### Clientes que mais compraram (nº de visitas)")
    top_clientes_frequencia = df_display.groupby('cliente')['venda_id'].nunique().nlargest(10).sort_values(ascending=True)

    if not top_clientes_frequencia.empty:
        st.bar_chart(top_clientes_frequencia, horizontal=True)
        st.info("💡 **Ação:** Estes são seus clientes mais leais e recorrentes. Eles são ótimos candidatos para dar feedback sobre novos produtos.")
    else:
        st.write("Não há dados de frequência para exibir.")


# --- Análise de Ticket Médio por Cliente ---
st.subheader("Ticket Médio por Cliente 💵")
st.markdown("Veja o valor médio que cada cliente gasta por visita. Use a busca para encontrar um cliente específico.")

try:
    valor_total_cliente = df_display.groupby('cliente')['valor_total'].sum()
    num_vendas_cliente = df_display.groupby('cliente')['venda_id'].nunique()
    ticket_medio_cliente = (valor_total_cliente / num_vendas_cliente).fillna(0).sort_values(ascending=False)

    # Preparar DataFrame para exibição
    df_ticket_medio = pd.DataFrame({
        'Ticket Médio (R$)': ticket_medio_cliente,
        'Valor Total Gasto (R$)': valor_total_cliente,
        'Total de Visitas': num_vendas_cliente
    }).reset_index()

    # Formatar colunas para melhor visualização
    df_ticket_medio['Ticket Médio (R$)'] = df_ticket_medio['Ticket Médio (R$)'].map('{:,.2f}'.format)
    df_ticket_medio['Valor Total Gasto (R$)'] = df_ticket_medio['Valor Total Gasto (R$)'].map('{:,.2f}'.format)
    
    st.dataframe(df_ticket_medio, use_container_width=True)

except Exception as e:
    st.error(f"Não foi possível calcular o ticket médio por cliente: {e}")