import pandas as pd
import sqlite3
import os

# __file__ é uma variavel q tem o caminho do arquivo do script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DB_NAME = os.path.join(PROJECT_ROOT, 'acai.db')
DATA_FOLDER = os.path.join(PROJECT_ROOT, 'data')
ARQUIVO_CSV_PRINCIPAL = 'dados_vendas_acai.csv'  # Defina o nome do seu CSV principal aqui

def conectar_bd():
    print(f"Tentando conectar ao banco de dados: {DB_NAME}")
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON;") # Habilitar checagem de FK
    print("Conexão estabelecida e chaves estrangeiras habilitadas.")
    return conn

def criar_tabelas(conn):
    cursor = conn.cursor()
    print("\n--- Criando Tabelas (se não existirem) ---")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categorias(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE NOT NULL
    )
    """)
    print("- Tabela 'categorias' verificada/criada.")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS formas_pagamento(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE NOT NULL
    )
    """)
    print("- Tabela 'formas_pagamento' verificada/criada.")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produtos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE NOT NULL,
        categoria_id INTEGER,
        FOREIGN KEY (categoria_id) REFERENCES categorias (id) ON DELETE SET NULL
    )
    """)
    print("- Tabela 'produtos' verificada/criada.")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vendas(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_venda TEXT NOT NULL, -- Formato 'YYYY-MM-DD HH:MM:SS'
        cliente TEXT NOT NULL,
        produto_id INTEGER NOT NULL,
        quantidade INTEGER NOT NULL,
        forma_pagamento_id INTEGER NOT NULL,
        preco_unitario REAL NOT NULL,
        valor_total REAL NOT NULL,
        FOREIGN KEY (produto_id) REFERENCES produtos (id) ON DELETE RESTRICT,
        FOREIGN KEY (forma_pagamento_id) REFERENCES formas_pagamento (id) ON DELETE RESTRICT
    )
    """)
    print("- Tabela 'vendas' verificada/criada.")

    conn.commit()
    print("--- Criação de tabelas concluída. ---")

def popular_tabela_lookup(conn, nome_tabela_sql, series_de_nomes_unicos, nome_coluna_sql='nome'):
    """
    Popula uma tabela de lookup simples (ex: categorias, formas_pagamento)
    a partir de uma série de nomes únicos.
    """
    print(f"\nPopulando tabela de lookup: '{nome_tabela_sql}'")
    try:
        if series_de_nomes_unicos.empty:
            print(f"  AVISO: Nenhuma série de nomes fornecida. Tabela '{nome_tabela_sql}' não populada.")
            return

        df_lookup = pd.DataFrame(series_de_nomes_unicos.unique(), columns=[nome_coluna_sql])
        df_lookup.dropna(subset=[nome_coluna_sql], inplace=True) # Remover NaNs se houver
        df_lookup = df_lookup[df_lookup[nome_coluna_sql].str.strip() != ''] # Remover strings vazias

        if df_lookup.empty:
            print(f"  AVISO: Nenhum valor único válido encontrado. Tabela '{nome_tabela_sql}' não populada.")
            return

        # Usar try-except para cada linha para lidar com 'UNIQUE constraint failed' individualmente
        # ou inserir tudo e capturar o erro (mais simples com pandas, mas menos granular)
        # Para simplicidade, df.to_sql com if_exists='append' vai tentar inserir.
        # Erros de UNIQUE serão levantados pelo SQLite se já existirem, o que é bom.
        try:
            df_lookup.to_sql(nome_tabela_sql, conn, if_exists='append', index=False)
            print(f"  SUCESSO (tentativa): Tabela '{nome_tabela_sql}' populada/atualizada com {len(df_lookup)} valores únicos.")
        except sqlite3.IntegrityError as ie:
            print(f"  INFO: Alguns ou todos os dados já podem existir em '{nome_tabela_sql}' (erro de integridade: {ie}). Isso é esperado se os dados já foram inseridos.")
        except Exception as e_to_sql:
            print(f"  ERRO ao usar to_sql para '{nome_tabela_sql}': {e_to_sql}")


    except Exception as e:
        print(f"  ERRO geral ao popular '{nome_tabela_sql}': {e}")


if __name__ == '__main__':
    print("--- Iniciando Script de Setup do Banco de Dados ---")
    conn = None
    try:
        conn = conectar_bd()
        criar_tabelas(conn)

        print("\n--- Normalizando e Populando Tabelas a partir do CSV Principal ---")
        caminho_csv_principal = os.path.join(DATA_FOLDER, ARQUIVO_CSV_PRINCIPAL)

        if not os.path.exists(caminho_csv_principal):
            print(f"  AVISO CRÍTICO: Arquivo CSV Principal '{ARQUIVO_CSV_PRINCIPAL}' NÃO ENCONTRADO em '{DATA_FOLDER}'.")
            print("  O script não pode popular as tabelas.")
        else:
            print(f"Lendo CSV Principal: {caminho_csv_principal}")
            # Ajuste dayfirst=True se suas datas no CSV são DD/MM/YYYY
            df_principal = pd.read_csv(caminho_csv_principal, parse_dates=['data_venda'], dayfirst=True)
            print(f"Lido CSV Principal. {len(df_principal)} linhas encontradas.")

            if df_principal.empty:
                print("  AVISO: O CSV Principal está vazio. Nada para popular.")
            else:
                # 1. Popular Categorias
                if 'categoria' in df_principal.columns:
                    popular_tabela_lookup(conn, 'categorias', df_principal['categoria'])
                else:
                    print("  AVISO: Coluna 'categoria' não encontrada no CSV principal. Tabela 'categorias' não populada.")

                # 2. Popular Formas de Pagamento
                if 'forma_pagamento' in df_principal.columns:
                    popular_tabela_lookup(conn, 'formas_pagamento', df_principal['forma_pagamento'])
                else:
                    print("  AVISO: Coluna 'forma_pagamento' não encontrada no CSV principal. Tabela 'formas_pagamento' não populada.")

                # 3. Popular Produtos (requer lookup de categoria_id)
                print("\nPopulando tabela 'produtos'...")
                if 'produto' in df_principal.columns and 'categoria' in df_principal.columns:
                    try:
                        df_categorias_bd = pd.read_sql_query("SELECT id, nome FROM categorias", conn)
                        map_categoria_id = df_categorias_bd.set_index('nome')['id'].to_dict()

                        df_produtos_source = df_principal[['produto', 'categoria']].copy()
                        df_produtos_source.drop_duplicates(subset=['produto'], inplace=True) # Pega cada produto uma vez
                        df_produtos_source['nome'] = df_produtos_source['produto'] # Renomeia para 'nome'
                        df_produtos_source['categoria_id'] = df_produtos_source['categoria'].map(map_categoria_id)
                        
                        df_produtos_final = df_produtos_source[['nome', 'categoria_id']].dropna(subset=['nome'])
                        df_produtos_final = df_produtos_final[df_produtos_final['nome'].str.strip() != '']


                        if df_produtos_final.empty:
                            print("  AVISO: Nenhum dado de produto válido para inserir após mapeamento.")
                        else:
                            try:
                                df_produtos_final.to_sql('produtos', conn, if_exists='append', index=False)
                                print(f"  SUCESSO (tentativa): Tabela 'produtos' populada/atualizada com {len(df_produtos_final)} produtos.")
                            except sqlite3.IntegrityError as ie:
                                print(f"  INFO: Alguns ou todos os produtos já podem existir (erro de integridade: {ie}).")
                            except Exception as e_to_sql:
                                print(f"  ERRO ao usar to_sql para 'produtos': {e_to_sql}")

                    except Exception as e_prod:
                        print(f"  ERRO ao preparar dados para 'produtos': {e_prod}")
                else:
                    print("  AVISO: Colunas 'produto' ou 'categoria' não encontradas. Tabela 'produtos' não populada.")


                # 4. Popular Vendas (requer lookup de produto_id e forma_pagamento_id)
                print("\nPopulando tabela 'vendas'...")
                if all(col in df_principal.columns for col in ['data_venda', 'cliente', 'produto', 'quantidade', 'forma_pagamento', 'preco_unitario', 'valor_total']):
                    try:
                        df_produtos_bd = pd.read_sql_query("SELECT id, nome FROM produtos", conn)
                        map_produto_id = df_produtos_bd.set_index('nome')['id'].to_dict()

                        df_formas_pagamento_bd = pd.read_sql_query("SELECT id, nome FROM formas_pagamento", conn)
                        map_forma_pagamento_id = df_formas_pagamento_bd.set_index('nome')['id'].to_dict()

                        df_vendas_preparado = df_principal.copy()
                        df_vendas_preparado['produto_id'] = df_vendas_preparado['produto'].map(map_produto_id)
                        df_vendas_preparado['forma_pagamento_id'] = df_vendas_preparado['forma_pagamento'].map(map_forma_pagamento_id)
                        
                        # Garantir que data_venda seja formatada como texto para SQLite
                        df_vendas_preparado['data_venda'] = pd.to_datetime(df_vendas_preparado['data_venda']).dt.strftime('%Y-%m-%d %H:%M:%S')

                        colunas_vendas_sql = ['data_venda', 'cliente', 'produto_id', 'quantidade',
                                              'forma_pagamento_id', 'preco_unitario', 'valor_total']
                        df_vendas_final = df_vendas_preparado[colunas_vendas_sql]
                        
                        # Verificar se há NaNs nas colunas de ID, o que indicaria falha no mapeamento
                        if df_vendas_final['produto_id'].isnull().any() or df_vendas_final['forma_pagamento_id'].isnull().any():
                            print("  AVISO: Algumas vendas não puderam ser mapeadas para IDs de produto ou forma_pagamento e não serão inseridas.")
                            print("  Verifique se todos os produtos e formas de pagamento do CSV de vendas existem nas respectivas tabelas de lookup.")
                            # Você pode querer ver quais falharam:
                            # print(df_vendas_preparado[df_vendas_preparado['produto_id'].isnull() | df_vendas_preparado['forma_pagamento_id'].isnull()])
                            df_vendas_final.dropna(subset=['produto_id', 'forma_pagamento_id'], inplace=True)


                        if df_vendas_final.empty:
                             print("  AVISO: Nenhum dado de venda válido para inserir após mapeamento e remoção de nulos.")
                        else:
                            try:
                                df_vendas_final.to_sql('vendas', conn, if_exists='append', index=False)
                                print(f"  SUCESSO: Tabela 'vendas' populada com {len(df_vendas_final)} registros.")
                            except sqlite3.IntegrityError as ie: # Menos provável aqui, a menos que você tenha uma UNIQUE constraint em vendas
                                print(f"  ERRO de integridade ao inserir em 'vendas': {ie}")
                            except Exception as e_to_sql:
                                print(f"  ERRO ao usar to_sql para 'vendas': {e_to_sql}")
                                
                    except Exception as e_vendas:
                        print(f"  ERRO ao preparar dados para 'vendas': {e_vendas}")
                else:
                    print("  AVISO: Colunas necessárias para 'vendas' não encontradas no CSV principal.")
    
    except sqlite3.Error as e_sqlite:
        print(f"ERRO SQLite durante o setup: {e_sqlite}")
    except FileNotFoundError as e_fnf:
        print(f"ERRO Arquivo não encontrado: {e_fnf}")
    except pd.errors.EmptyDataError as e_ede:
        print(f"ERRO Dados vazios no CSV: {e_ede}")
    except Exception as e_geral:
        print(f"ERRO GERAL durante o setup: {e_geral}")
    finally:
        if conn:
            conn.close()
            print(f"\nConexão com o banco de Dados '{DB_NAME}' fechada.")
    print("--- Script de Setup Finalizado. ---")