import streamlit as st
import pandas as pd
import os

# -----------------------------
# Funções utilitárias
# -----------------------------
def carregar_csv(nome_arquivo):
    """Carrega CSV com detecção de codificação, separador e normalização"""
    if not os.path.exists(nome_arquivo):
        pd.DataFrame().to_csv(nome_arquivo, index=False, encoding="utf-8")

    try:
        # tenta UTF-8 com vírgula
        df = pd.read_csv(nome_arquivo, encoding="utf-8", sep=",")
    except UnicodeDecodeError:
        # tenta Latin1
        try:
            df = pd.read_csv(nome_arquivo, encoding="latin1", sep=",")
        except Exception:
            # tenta Latin1 com ponto e vírgula
            df = pd.read_csv(nome_arquivo, encoding="latin1", sep=";")
    except pd.errors.ParserError:
        # tenta UTF-8 com ponto e vírgula
        df = pd.read_csv(nome_arquivo, encoding="utf-8", sep=";")

    # Normaliza nomes das colunas
    df.columns = df.columns.astype(str)
    df.columns = df.columns.str.strip().str.replace(" ", "_").str.lower()
    return df


def salvar_csv(df, nome_arquivo):
    """Salva CSV em UTF-8"""
    df.to_csv(nome_arquivo, index=False, encoding="utf-8")


def encontrar_coluna(df, termos):
    """Tenta encontrar uma coluna cujo nome contenha um dos termos"""
    for termo in termos:
        matches = [c for c in df.columns if termo in c.lower()]
        if matches:
            return matches[0]
    return None


# -----------------------------
# Carregar bases
# -----------------------------
ambientes_df = carregar_csv("base_ambientes.csv")
caixas_df = carregar_csv("base_caixas.csv")
clientes_df = carregar_csv("clientes.csv")
projetos_df = carregar_csv("projetos.csv")

# -----------------------------
# Detectar colunas de interesse
# -----------------------------
col_cliente = encontrar_coluna(clientes_df, ["nome", "cliente"])
col_ambiente = encontrar_coluna(ambientes_df, ["nome", "ambiente"])
col_caixa = encontrar_coluna(caixas_df, ["nome", "modelo", "caixa"])

# -----------------------------
# Criar listas seguras
# -----------------------------
clientes = clientes_df[col_cliente].tolist() if col_cliente else []
ambientes = ambientes_df[col_ambiente].tolist() if col_ambiente else []
caixas = caixas_df[col_caixa].tolist() if col_caixa else []

# -----------------------------
# Interface Streamlit
# -----------------------------
st.set_page_config(page_title="AcousticCalc Web", layout="wide")
st.title("🎵 AcousticCalc Web - Sistema de Sonorização")

interface_toggle = st.checkbox("Interface Resumida (toggle)")

if interface_toggle:
    st.info("🟢 Interface resumida ativada")
else:
    st.info("🔵 Interface completa ativada")

# -----------------------------
# Avisos se faltar alguma coluna
# -----------------------------
if not col_cliente:
    st.warning("⚠️ Nenhuma coluna de nome/cliente encontrada em clientes.csv")
if not col_ambiente:
    st.warning("⚠️ Nenhuma coluna de nome/ambiente encontrada em base_ambientes.csv")
if not col_caixa:
    st.warning("⚠️ Nenhuma coluna de nome/modelo/caixa encontrada em base_caixas.csv")

# -----------------------------
# Formulário principal
# -----------------------------
with st.form("form_projeto"):
    cliente_sel = st.selectbox("Selecione o cliente", clientes)
    ambiente_sel = st.selectbox("Selecione o ambiente", ambientes)
    caixa_sel = st.selectbox("Selecione o equipamento", caixas)
    submit = st.form_submit_button("Salvar projeto")

if submit:
    novo = pd.DataFrame([{
        "Cliente": cliente_sel,
        "Ambiente": ambiente_sel,
        "Caixa": caixa_sel
    }])
    projetos_df = pd.concat([projetos_df, novo], ignore_index=True)
    salvar_csv(projetos_df, "projetos.csv")
    st.success("✅ Projeto salvo com sucesso!")

# -----------------------------
# Exibir tabelas carregadas
# -----------------------------
st.subheader("📊 Bases carregadas")
with st.expander("Clientes"):
    st.dataframe(clientes_df)
with st.expander("Ambientes"):
    st.dataframe(ambientes_df)
with st.expander("Caixas"):
    st.dataframe(caixas_df)
with st.expander("Projetos"):
    st.dataframe(projetos_df)
