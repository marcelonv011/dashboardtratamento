import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title="Dashboard Consumidor.gov.br",
    layout="wide"
)

st.title("Dashboard — Qualidade do Atendimento ao Consumidor")
st.write("Consumidor.gov.br — Março/2026")

# Carregamento da base
df = pd.read_csv("consumidores_final.csv", sep=";")

# Conversão de colunas numéricas
df["tempo_resposta"] = pd.to_numeric(df["tempo_resposta"], errors="coerce")
df["nota_do_consumidor"] = pd.to_numeric(df["nota_do_consumidor"], errors="coerce")
df["reclamacao_resolvida"] = pd.to_numeric(df["reclamacao_resolvida"], errors="coerce")

# Sidebar - filtros
st.sidebar.header("Filtros")

segmentos = ["Todos"] + sorted(df["segmento_de_mercado"].dropna().unique())
segmento = st.sidebar.selectbox("Segmento de Mercado", segmentos)

ufs = ["Todos"] + sorted(df["uf"].dropna().unique())
uf = st.sidebar.selectbox("UF", ufs)

if segmento != "Todos":
    df = df[df["segmento_de_mercado"] == segmento]

if uf != "Todos":
    df = df[df["uf"] == uf]

# KPIs
taxa_resolucao = df["reclamacao_resolvida"].mean() * 100
tempo_medio = df["tempo_resposta"].mean()
nota_media = df["nota_do_consumidor"].mean()
volume = len(df)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Taxa de Resolução", f"{taxa_resolucao:.1f}%")
col2.metric("Tempo Médio de Resposta", f"{tempo_medio:.1f} dias")
col3.metric("Nota Média", f"{nota_media:.2f}")
col4.metric("Volume de Reclamações", f"{volume:,}".replace(",", "."))

st.divider()

# Gráfico 1
st.subheader("1. Volume e Taxa de Resolução por Segmento")

df["resolvida_label"] = df["reclamacao_resolvida"].map({
    0: "Não resolvida",
    1: "Resolvida"
})

top_segmentos = df["segmento_de_mercado"].value_counts().nlargest(10).index
df_top = df[df["segmento_de_mercado"].isin(top_segmentos)]

fig1, ax1 = plt.subplots(figsize=(12, 6))
sns.countplot(
    data=df_top,
    y="segmento_de_mercado",
    hue="resolvida_label",
    ax=ax1
)
ax1.set_xlabel("Quantidade de Reclamações")
ax1.set_ylabel("Segmento de Mercado")
ax1.set_title("Volume e Resolução por Segmento de Mercado — Top 10")
ax1.legend(title="Situação")
plt.tight_layout()
st.pyplot(fig1)

# Gráfico 2
st.subheader("2. Tempo Médio de Resposta por Segmento")

tempo_medio_top10 = (
    df_top
    .groupby("segmento_de_mercado")["tempo_resposta"]
    .mean()
    .sort_values()
)

fig2, ax2 = plt.subplots(figsize=(12, 6))
tempo_medio_top10.plot(kind="barh", ax=ax2)
ax2.set_xlabel("Tempo Médio de Resposta (dias)")
ax2.set_ylabel("Segmento de Mercado")
ax2.set_title("Tempo Médio de Resposta por Segmento — Top 10")
plt.tight_layout()
st.pyplot(fig2)

# Gráfico 3
st.subheader("3. Distribuição da Satisfação por Faixa de Tempo de Resposta")

ordem_tempo = [
    "Rápido (0–2 dias)",
    "Moderado (3–5 dias)",
    "Lento (6–8 dias)",
    "Muito Lento (9–11 dias)"
]

ordem_satisfacao = [
    "Insatisfeito (1–2)",
    "Neutro (3)",
    "Satisfeito (4–5)"
]

crosstab_pct = pd.crosstab(
    df["faixa_tempo_resposta"],
    df["faixa_satisfacao"],
    normalize="index"
) * 100

crosstab_pct = crosstab_pct.reindex(ordem_tempo)
crosstab_pct = crosstab_pct.reindex(columns=ordem_satisfacao)

fig3, ax3 = plt.subplots(figsize=(12, 6))
crosstab_pct.plot(kind="bar", stacked=True, ax=ax3)
ax3.set_ylabel("Percentual de Reclamações (%)")
ax3.set_xlabel("Faixa de Tempo de Resposta")
ax3.set_title("Satisfação do Consumidor por Tempo de Resposta")
ax3.legend(title="Faixa de Satisfação")
plt.xticks(rotation=20)
plt.tight_layout()
st.pyplot(fig3)

st.divider()

st.caption(
    "Dashboard desenvolvido para análise da qualidade do atendimento ao consumidor "
    "com base em dados do Consumidor.gov.br"
)