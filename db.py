import mysql.connector
import pandas as pd

def conectar(host='localhost', user='root', password='root', database='dw_combustiveis_v4'):
    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )

def carregar_dados(con=None):
    # Se não passar conexão, cria uma local
    if con is None:
        con = conectar()
    query = """
    SELECT
        f.id_posto,
        f.id_combustivel,
        f.id_tempo,
        f.CEP,
        f.Valor_venda,
        f.ICMS_Medio,
        f.Impacto_ICMS,
        f.Valor_Producao_Petroleo,
        f.Unidade,
        p.Nome_posto,
        p.Bandeira,
        p.CNPJ AS CNPJ_posto,
        l.CEP AS cep_local,
        l.Bairro,
        l.Municipio,
        l.Estado AS estado_localizacao,
        l.Regiao,
        c.Tipo_combustivel,
        c.Especificacao,
        t.Data AS data_transacao,
        t.Ano,
        t.Mes,
        t.Trimestre,
        t.Semana
    FROM fato_vendas_icms f
    LEFT JOIN dim_posto p ON f.id_posto = p.id_posto
    LEFT JOIN dim_localizacao l ON f.CEP = l.CEP
    LEFT JOIN dim_combustivel c ON f.id_combustivel = c.id_combustivel
    LEFT JOIN dim_tempo t ON f.id_tempo = t.id_tempo
    ;
    """
    df = pd.read_sql(query, con)
    df.columns = [c.strip() for c in df.columns]
    return df


# -------------------------------------------------------------------
# ✅ ALIAS para compatibilidade com o app.py
# -------------------------------------------------------------------

def load_data():
    """Mantém compatibilidade com o app.py"""
    return carregar_dados()
