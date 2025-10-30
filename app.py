import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import math
import os

# ------------------------------------------------------------
# 🧩 Configurações iniciais
# ------------------------------------------------------------
st.set_page_config(page_title="AcousticCalc Web", page_icon="🎧", layout="wide")
st.title("🎧 AcousticCalc Web")
st.caption("Dimensionamento Sonoro e Análise Acústica Inteligente")

# Toggle Interface
modo_completo = st.toggle("🔀 Modo Completo", value=True, help="Ative para exibir todos os parâmetros técnicos")

# ------------------------------------------------------------
# 📁 Funções auxiliares
# ------------------------------------------------------------
def carregar_csv(nome_arquivo):
    import io
    if not os.path.exists(nome_arquivo):
        pd.DataFrame().to_csv(nome_arquivo, index=False)
    try:
        return pd.read_csv(nome_arquivo, encoding="utf-8")
    except UnicodeDecodeError:
        # Caso o arquivo tenha sido salvo em ANSI ou Latin1
        return pd.read_csv(nome_arquivo, encoding="latin1")

    # Normaliza os nomes das colunas
    df.columns = df.columns.str.strip()           # remove espaços extras
    df.columns = df.columns.str.replace(" ", "_") # substitui espaços por underline
    df.columns = df.columns.str.title()           # primeira letra maiúscula
    return df
    
# ------------------------------------------------------------
# 🔍 Carregando bases
# ------------------------------------------------------------
ambientes_df = carregar_csv("base_ambientes.csv")
caixas_df = carregar_csv("base_caixas.csv")
clientes_df = carregar_csv("clientes.csv")
projetos_df = carregar_csv("projetos.csv")

# ------------------------------------------------------------
# 🧮 Seção principal – cálculo
# ------------------------------------------------------------
st.header("📊 Novo Projeto")

# Cliente
st.subheader("Cliente")
clientes = clientes_df["Nome"].tolist()
cliente_sel = st.selectbox("Selecione o cliente", clientes)
if st.button("➕ Novo Cliente"):
    with st.form("novo_cliente"):
        nome = st.text_input("Nome do Cliente")
        contato = st.text_input("Contato (telefone/email)")
        endereco = st.text_input("Endereço")
        cidade = st.text_input("Cidade")
        estado = st.text_input("Estado")
        enviar = st.form_submit_button("Salvar")
        if enviar:
            novo_id = f"C{len(clientes_df)+1:03d}"
            clientes_df.loc[len(clientes_df)] = [novo_id,nome,contato,endereco,cidade,estado]
            salvar_csv(clientes_df,"clientes.csv")
            st.success("Cliente salvo!")

# Ambiente
st.subheader("Ambiente")
ambiente_sel = st.selectbox("Selecione o tipo de ambiente", ambientes_df["Nome"])
if st.button("➕ Novo Ambiente"):
    with st.form("novo_ambiente"):
        nome = st.text_input("Nome do Ambiente")
        spl = st.number_input("SPL alvo (dB)",60,110,85)
        rt60 = st.number_input("RT60 alvo (s)",0.2,3.0,1.0,step=0.1)
        abs_m = st.number_input("Coeficiente médio de absorção",0.1,1.0,0.3,step=0.05)
        cob = st.number_input("Cobertura padrão (m²)",10,200,40)
        enviar = st.form_submit_button("Salvar")
        if enviar:
            ambientes_df.loc[len(ambientes_df)] = [nome,spl,rt60,abs_m,cob]
            salvar_csv(ambientes_df,"base_ambientes.csv")
            st.success("Ambiente adicionado!")

# Caixa
st.subheader("Equipamento")
caixa_sel = st.selectbox("Selecione o modelo de caixa", caixas_df["Modelo"])
if st.button("➕ Nova Caixa"):
    with st.form("nova_caixa"):
        marca = st.text_input("Marca")
        modelo = st.text_input("Modelo")
        tipo = st.text_input("Tipo (ativa/passiva, tamanho)")
        sens = st.number_input("Sensibilidade (dB/W/m)",80,110,95)
        pot = st.number_input("Potência RMS (W)",50,5000,300)
        cob = st.number_input("Cobertura (m²)",5,200,35)
        enviar = st.form_submit_button("Salvar")
        if enviar:
            caixas_df.loc[len(caixas_df)] = [marca,modelo,tipo,sens,pot,cob]
            salvar_csv(caixas_df,"base_caixas.csv")
            st.success("Caixa adicionada!")

# Parâmetros geométricos
st.subheader("Dimensões do ambiente")
col1, col2, col3 = st.columns(3)
compr = col1.number_input("Comprimento (m)",5.0,100.0,20.0)
larg = col2.number_input("Largura (m)",5.0,100.0,10.0)
alt = col3.number_input("Pé-direito (m)",2.0,10.0,3.0)

area = compr * larg
volume = area * alt

# Dados selecionados
amb_data = ambientes_df.loc[ambientes_df["Nome"]==ambiente_sel].iloc[0]
cx_data = caixas_df.loc[caixas_df["Modelo"]==caixa_sel].iloc[0]

# Cálculo SPL e potência
spl_desejado = amb_data["SPL_alvo"]
dist_media = compr/2
perda = 20*np.log10(dist_media)
spl_ajust = cx_data["Sensibilidade"] + 10*np.log10(cx_data["Potencia_RMS"]) - perda
dif_db = max(spl_desejado - spl_ajust, 0)
pot_necessaria = cx_data["Potencia_RMS"] * (2**(dif_db/3))
num_caixas = math.ceil(area / cx_data["Cobertura_m2"])
pot_total = pot_necessaria * num_caixas

# RT60
alpha = amb_data["Absorcao_media"]
rt60 = 0.161 * (volume / (area * alpha))
if rt60 > 1.5: classe = "🟨 Reverberação Alta"
elif rt60 < 0.4: classe = "🟦 Ambiente Seco"
else: classe = "🟩 Acústica Adequada"

# ------------------------------------------------------------
# 🧾 Resultados
# ------------------------------------------------------------
st.markdown("---")
st.header("📈 Resultados")

if modo_completo:
    st.metric("Área (m²)", f"{area:.1f}")
    st.metric("Volume (m³)", f"{volume:.1f}")
    st.metric("Perda sonora (dB)", f"{perda:.1f}")

col1, col2 = st.columns(2)
col1.metric("SPL ajustado", f"{spl_ajust:.1f} dB")
col1.metric("Caixas necessárias", int(num_caixas))
col2.metric("Potência total", f"{pot_total:.0f} W")
col2.metric("RT60", f"{rt60:.2f} s")

st.success(f"Classificação: {classe}")

# ------------------------------------------------------------
# 💾 Salvamento do projeto
# ------------------------------------------------------------
if st.button("💾 Salvar Projeto"):
    cliente_id = clientes_df.loc[clientes_df["Nome"]==cliente_sel, "Cliente_ID"].values[0]
    proj_id = f"P{len(projetos_df)+1:03d}"
    novos_dados = [proj_id,cliente_id,ambiente_sel,cx_data["Modelo"],spl_desejado,spl_ajust,
                   pot_total,rt60,classe,datetime.now().strftime("%Y-%m-%d")]
    projetos_df.loc[len(projetos_df)] = novos_dados
    salvar_csv(projetos_df,"projetos.csv")
    st.success("Projeto salvo com sucesso!")

# ------------------------------------------------------------
# 📂 Projetos existentes
# ------------------------------------------------------------
st.markdown("---")
st.header("📁 Projetos Salvos")
if not projetos_df.empty:
    st.dataframe(projetos_df[["Projeto_ID","Ambiente","Caixa","Classificacao","Data"]])
else:
    st.info("Nenhum projeto salvo ainda.")


