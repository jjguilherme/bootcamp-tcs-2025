import streamlit as st 
import pandas as pd
import sqlite3 
from datetime import datetime, timedelta 

DB_NAME = 'acai.db'

@st.cache_data # Cache para otimizar o carregamento
def carregar_dados_base(start_date, end_date, formas_pagamento_selecionadas=None, clientes_selecionados=None):
    conn = sqlite3.connect(DB_NAME)
    # Ajustar end_date para incluir o dia todo
    end_date_sql = (pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)).strftime('%Y-%m-%d %H:%M:%S')
    start_date_sql = pd.to_datetime(start_date).strftime('%Y-%m-%d %H:%M:%S')

    query = """
        SELECT
            v.id as venda_id, v.data_venda, v.cliente, v.quantidade, v.preco_unitario, v.valor_total,
            p.nome as produto_nome,
            c.nome as categoria_nome,
            fp.nome as forma_pagamento_nome
        FROM vendas v
        JOIN produtos p ON v.produto_id = p.id
        JOIN categorias c ON p.categoria_id = c.id
        JOIN formas_pagamento fp ON v.forma_pagamento_id = fp.id
        WHERE v.data_venda BETWEEN ? AND ?
    """
    params = [start_date_sql, end_date_sql]

    if formas_pagamento_selecionadas:
        placeholders = ','.join(['?'] * len(formas_pagamento_selecionadas))
        query += f" AND fp.nome IN ({placeholders})"
        params.extend(formas_pagamento_selecionadas)

    if clientes_selecionados:
        placeholders = ','.join(['?'] * len(clientes_selecionados))
        query += f" AND v.cliente IN ({placeholders})"
        params.extend(clientes_selecionados)

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    if not df.empty:
        df['data_venda'] = pd.to_datetime(df['data_venda'])
    return df

@st.cache_data
def obter_opcoes_filtro():
    conn = sqlite3.connect(DB_NAME)
    formas_pagamento = pd.read_sql_query("SELECT DISTINCT nome FROM formas_pagamento ORDER BY nome", conn)['nome'].tolist()
    clientes = pd.read_sql_query("SELECT DISTINCT cliente FROM vendas ORDER BY cliente", conn)['cliente'].tolist()
    min_max_data = pd.read_sql_query("SELECT MIN(data_venda) as min_d, MAX(data_venda) as max_d FROM vendas", conn)
    conn.close()
    min_date = pd.to_datetime(min_max_data['min_d'][0]) if not min_max_data.empty and min_max_data['min_d'][0] else datetime.now() - timedelta(days=30)
    max_date = pd.to_datetime(min_max_data['max_d'][0]) if not min_max_data.empty and min_max_data['max_d'][0] else datetime.now()
    return formas_pagamento, clientes, min_date, max_date

def adicionar_colunas_derivadas(df):
    if df is None or df.empty:
        return pd.DataFrame() # Retorna DAtaframe vazio se o input for None ou vazio
    df_copy = df.copy()
    df_copy['hora_venda'] = df_copy['data_venda'].dt.hour
    df_copy['dia_semana_venda'] = df_copy['data_venda'].dt.day_name()
    df_copy['mes_ano_venda'] = df_copy['data_venda'].dt.to_period('M').astype(str)
    return df_copy