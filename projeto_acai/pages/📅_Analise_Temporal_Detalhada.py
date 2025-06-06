# pages/📅_Analise_Temporal_Detalhada.py
import streamlit as st
import pandas as pd

# Define o layout da página e o título que aparece na aba do navegador
#st.set_page_config(layout="wide", page_title="Análise Temporal")

# Título principal da página
st.title("Análise Temporal Detalhada 📅")

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


# --- Análise de Vendas por Hora do Dia ---
st.subheader("Vendas por Hora do Dia ⏰")
st.markdown("Identifique os horários de pico para otimizar a escala de sua equipe e o preparo dos produtos.")

# Agrupar por hora e somar o valor total
vendas_por_hora = df_display.groupby('hora_venda')['valor_total'].sum()

if not vendas_por_hora.empty:
    # Encontrar a hora com o maior valor de vendas
    hora_pico_valor = vendas_por_hora.idxmax()
    
    col1, col2 = st.columns([2, 1]) # Criar duas colunas, a primeira com 2/3 do espaço
    with col1:
        st.bar_chart(vendas_por_hora)
    with col2:
        st.metric("Horário de Pico (Maior Faturamento)", f"{hora_pico_valor}:00 - {hora_pico_valor+1}:00")
        st.info(f"💡 **Ação:** Considere reforçar sua equipe ou preparar mais ingredientes um pouco antes das **{hora_pico_valor}h** para garantir um atendimento rápido durante o pico de movimento.")
else:
    st.write("Não há dados suficientes para analisar as vendas por hora.")


# --- Análise de Vendas por Dia da Semana ---
st.subheader("Vendas por Dia da Semana 🗓️")
st.markdown("Entenda o ritmo do seu negócio ao longo da semana para planejar promoções e folgas.")

# Agrupar por dia da semana e somar o valor total
vendas_dia_semana = df_display.groupby('dia_semana_venda')['valor_total'].sum()

if not vendas_dia_semana.empty:
    # Ordenar os dias da semana corretamente (não em ordem alfabética)
    dias_ordem = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    nomes_pt = {"Monday": "Segunda", "Tuesday": "Terça", "Wednesday": "Quarta", "Thursday": "Quinta", "Friday": "Sexta", "Saturday": "Sábado", "Sunday": "Domingo"}
    
    vendas_dia_semana = vendas_dia_semana.reindex(dias_ordem, fill_value=0)
    vendas_dia_semana.index = vendas_dia_semana.index.map(nomes_pt) # Traduzir para português

    dia_mais_forte = vendas_dia_semana.idxmax()
    
    col_grafico, col_info = st.columns([2, 1])
    with col_grafico:
        st.bar_chart(vendas_dia_semana)
    with col_info:
        st.metric("Dia Mais Forte em Vendas", dia_mais_forte)
        st.info(f"💡 **Ação:** A **{dia_mais_forte}** é seu dia de maior faturamento. Crie promoções especiais para os dias de menor movimento para atrair mais clientes durante a semana.")
else:
    st.write("Não há dados suficientes para analisar as vendas por dia da semana.")

# --- Análise Mês a Mês (MoM) ---
with st.expander("Ver Análise Comparativa Mês a Mês (MoM)"):
    st.subheader("Comparativo Mês a Mês 📊")
    st.markdown("Acompanhe o crescimento do seu faturamento ao longo dos meses.")

    # Agrupar por mês/ano e somar o valor total
    vendas_por_mes = df_display.groupby('mes_ano_venda')['valor_total'].sum().sort_index()

    if len(vendas_por_mes) >= 2:
        # Pega os dados dos dois últimos meses disponíveis no período filtrado
        mes_atual_dados = vendas_por_mes.iloc[-1]
        mes_anterior_dados = vendas_por_mes.iloc[-2]
        
        # Calcula a variação percentual
        variacao_percentual = ((mes_atual_dados - mes_anterior_dados) / mes_anterior_dados) * 100 if mes_anterior_dados > 0 else float('inf')

        # Exibir métricas comparativas
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric(f"Vendas {vendas_por_mes.index[-1]}", f"R$ {mes_atual_dados:,.2f}")
        col_m2.metric(f"Vendas {vendas_por_mes.index[-2]}", f"R$ {mes_anterior_dados:,.2f}")
        col_m3.metric("Variação % (vs Mês Anterior)", f"{variacao_percentual:.2f}%")

        # Gráfico de barras com a evolução mensal
        st.markdown("##### Evolução Mensal do Faturamento")
        st.bar_chart(vendas_por_mes)
        
    elif len(vendas_por_mes) == 1:
        st.metric(f"Vendas {vendas_por_mes.index[0]}", f"R$ {vendas_por_mes.iloc[0]:,.2f}")
        st.info("Não há dados suficientes para comparação com o mês anterior no período selecionado.")
    else:
        st.warning("Não há dados de vendas mensais suficientes no período selecionado.")

# --- Análise Ano a Ano (YoY) ---
# Esta análise só faz sentido se houver dados de múltiplos anos
df_display['ano_venda'] = df_display['data_venda'].dt.year
if df_display['ano_venda'].nunique() >= 2:
    with st.expander("Ver Análise Ano a Ano (YoY)"):
        st.subheader("Comparativo Ano a Ano (YoY) 📈")
        st.markdown("Compare o desempenho de meses específicos entre anos diferentes.")

        # Preparar dados para o pivot
        df_display['mes_nome'] = df_display['data_venda'].dt.strftime('%B') # Nome do mês
        meses_ordem_yoy = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        meses_pt_yoy = {"January": "Jan", "February": "Fev", "March": "Mar", "April": "Abr", "May": "Mai", "June": "Jun", "July": "Jul", "August": "Ago", "September": "Set", "October": "Out", "November": "Nov", "December": "Dez"}
        
        # Criar a tabela pivot
        vendas_yoy = pd.pivot_table(
            df_display,
            values='valor_total',
            index='mes_nome',
            columns='ano_venda',
            aggfunc='sum',
            fill_value=0
        )
        
        # Ordenar os meses corretamente
        vendas_yoy = vendas_yoy.reindex(meses_ordem_yoy).dropna()
        vendas_yoy.index = vendas_yoy.index.map(meses_pt_yoy)

        if not vendas_yoy.empty:
            st.bar_chart(vendas_yoy)
            st.info("💡 **Análise:** Este gráfico é excelente para identificar crescimento sazonal. Por exemplo, você pode ver se as vendas de Dezembro deste ano foram melhores que as do ano passado.")
        else:
            st.write("Não foi possível gerar a comparação YoY com os dados selecionados.")