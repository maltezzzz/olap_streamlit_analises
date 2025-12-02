import streamlit as st
import pandas as pd
from db import load_data
from olap_engine import OlapEngine
import charts
import plotly.express as px

st.set_page_config(page_title="OLAP de Combustíveis", layout="wide")

st.title("📊 OLAP — Análises de Combustíveis e ICMS")

df = load_data()
olap = OlapEngine(df)

analysis = st.sidebar.selectbox(
    "Selecione a Análise OLAP",
    [
        "1 - Vendas por Tipo de Combustível e Ano",
        "2 - ICMS Médio por Estado e Município",
        "3 - Impacto do ICMS por Posto e Bandeira",
        "4 - Venda total por Região e Mês",
        "5 - Especificações dentro do mesmo combustível",
        "6 - Produção Nacional por Região e Ano",
        "7 - Ticket Médio por Posto"
    ]
)

# ----------------------------- ANALISE 1 -----------------------------
if analysis.startswith("1"):
    st.header("🟧 1 — Vendas por Tipo de Combustível e Ano")

    pivot = olap.pivot(
        index="Ano",
        columns="Tipo_combustivel",
        values="Valor_venda",
        aggfunc="sum"
    )

    st.plotly_chart(charts.stacked_line(pivot), use_container_width=True)
    st.dataframe(pivot)

# ----------------------------- ANALISE 2 -----------------------------
elif analysis.startswith("2"):
    st.header("🔷 2 — ICMS Médio por Estado e Município")

    # Pivot da tabela
    pivot = olap.pivot(
        index="estado_localizacao",
        columns="Municipio",
        values="ICMS_Medio",
        aggfunc="mean"
    )

    # Usa o DataFrame interno do OLAP Engine
    df = olap.df.copy()

    import plotly.express as px

    # Boxplot por Estado
    fig = px.box(
        df,
        x="estado_localizacao",
        y="ICMS_Medio",
        points=False,
        title="Distribuição do ICMS Médio por Estado"
    )

    fig.update_layout(
        xaxis_title="Estado",
        yaxis_title="ICMS Médio",
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)

    # Mostra tabela pivotada
    st.subheader("📋 Tabela Dinâmica (Estado x Município)")
    st.dataframe(pivot)

# ----------------------------- ANALISE 3 -----------------------------
elif analysis.startswith("3"):
    st.header("🟩 3 — Impacto do ICMS por Posto e Bandeira")

    pivot = olap.pivot(
        index="Bandeira",
        columns="Nome_posto",
        values="Impacto_ICMS",
        aggfunc="sum"
    )

    st.plotly_chart(charts.horizontal_bar(pivot.sum(axis=1)), use_container_width=True)
    st.dataframe(pivot)

# ----------------------------- ANALISE 4 -----------------------------
elif analysis.startswith("4"):
    st.header("🟪 4 — Venda total por Região e Mês")

    pivot = olap.pivot(
        index="Mes",
        columns="Regiao",
        values="Valor_venda",
        aggfunc="sum"
    )

    st.plotly_chart(charts.line_per_region(pivot), use_container_width=True)
    st.dataframe(pivot)

# ----------------------------- ANALISE 5 -----------------------------
elif analysis.startswith("5"):
    st.header("🟥 5 — Vendas por Tipo de Combustível e Bandeira")

    # pega DF real do OlapEngine
    df = olap.df.copy()

    # Colunas esperadas
    expected = ["Tipo_combustivel", "Bandeira", "Valor_venda"]
    missing = [c for c in expected if c not in df.columns]
    if missing:
        st.error(f"Colunas faltando para a análise 5: {missing}")
        st.write("Colunas disponíveis:", df.columns.tolist())
    else:
        # Limpeza básica: remover nulos nos campos-chave
        df = df.dropna(subset=["Tipo_combustivel", "Bandeira", "Valor_venda"])

        # Pivot para exibição tabular (opcional)
        pivot = df.pivot_table(
            index="Tipo_combustivel",
            columns="Bandeira",
            values="Valor_venda",
            aggfunc="sum",
            fill_value=0
        )

        st.subheader("📋 Tabela Dinâmica (Tipo de Combustível x Bandeira)")
        st.dataframe(pivot)

        # Agregação para gráfico — sumariza por Tipo x Bandeira
        df_plot = df.groupby(["Tipo_combustivel", "Bandeira"], as_index=False)["Valor_venda"].sum()

        # Se houver muitas bandeiras, opcional: escolher TOP N por soma total
        # Ajuste top_n conforme quiser; aqui deixo 10 como padrão
        top_n = st.sidebar.number_input("Mostrar TOP N Bandeiras (por soma total)", min_value=3, max_value=50, value=10, step=1)
        # calcular bandeiras top
        top_bandeiras = (
            df_plot.groupby("Bandeira", as_index=False)["Valor_venda"]
            .sum()
            .sort_values("Valor_venda", ascending=False)
            .head(top_n)["Bandeira"]
            .tolist()
        )

        # filtrar apenas top bandeiras para deixar o gráfico legível
        df_plot_top = df_plot[df_plot["Bandeira"].isin(top_bandeiras)].copy()

        import plotly.express as px

        fig = px.bar(
            df_plot_top,
            x="Tipo_combustivel",
            y="Valor_venda",
            color="Bandeira",
            barmode="group",
            title=f"Vendas por Tipo de Combustível por Bandeira — TOP {top_n} Bandeiras"
        )

        fig.update_layout(
            xaxis_title="Tipo de Combustível",
            yaxis_title="Valor Total de Vendas",
            height=600,
            legend_title="Bandeira"
        )

        st.plotly_chart(fig, use_container_width=True)

# ----------------------------- ANALISE 6 -----------------------------
elif analysis.startswith("6"):
    st.header("🟫 6 — Produção Nacional de Petróleo: Total e Participação Regional")

    # Usa o DataFrame interno do mecanismo OLAP
    df = olap.df.copy()

    # GARANTE QUE NÃO HÁ REGIÕES FALTANDO
    df["Regiao"] = df["Regiao"].fillna("Não Informado")

    # ➤ 1. PRODUÇÃO TOTAL NACIONAL POR ANO
    total_por_ano = (
        df.groupby("Ano")["Valor_Producao_Petroleo"]
        .sum()
        .rename("Total_Nacional")
        .to_frame()
    )

    # ➤ 2. PRODUÇÃO POR REGIÃO E ANO
    prod_regiao = (
        df.pivot_table(
            index="Ano",
            columns="Regiao",
            values="Valor_Producao_Petroleo",
            aggfunc="sum",
            fill_value=0
        )
    )

    # ➤ 3. PARTICIPAÇÃO % POR REGIÃO
    participacao = prod_regiao.div(prod_regiao.sum(axis=1), axis=0) * 100
    participacao = participacao.round(2)

    # ------------- GRÁFICOS ----------------

    st.subheader("📈 Produção Total Nacional por Ano")
    st.plotly_chart(charts.line(total_por_ano), use_container_width=True)

    st.subheader("🗺️ Participação Percentual das Regiões")
    st.plotly_chart(charts.area_stacked(participacao), use_container_width=True)

    # ------------- TABELAS ----------------

    st.subheader("📊 Tabelas Detalhadas")

    st.markdown("**Produção total por ano:**")
    st.dataframe(total_por_ano)

    st.markdown("**Participação (%) das regiões:**")
    st.dataframe(participacao)

    st.markdown("**Produção por região (valores absolutos):**")
    st.dataframe(prod_regiao)


# ----------------------------- ANALISE 7 -----------------------------
elif analysis.startswith("7"):
    st.header("🟦 7 — Ticket Médio por Posto")

    pivot = df.groupby("Nome_posto")["Valor_venda"].mean().sort_values(ascending=False)

    st.plotly_chart(charts.horizontal_topN(pivot), use_container_width=True)
    st.dataframe(pivot)
