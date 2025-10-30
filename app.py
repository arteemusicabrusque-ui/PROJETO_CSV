import streamlit as st

import pandas as pd

import numpy as np

from datetime import datetime

import math

import os



\# ------------------------------------------------------------

\# 🧩 Configurações iniciais

\# ------------------------------------------------------------

st.set\_page\_config(page\_title="AcousticCalc Web", page\_icon="🎧", layout="wide")

st.title("🎧 AcousticCalc Web")

st.caption("Dimensionamento Sonoro e Análise Acústica Inteligente")



\# Toggle Interface

modo\_completo = st.toggle("🔀 Modo Completo", value=True, help="Ative para exibir todos os parâmetros técnicos")



\# ------------------------------------------------------------

\# 📁 Funções auxiliares

\# ------------------------------------------------------------

def carregar\_csv(nome\_arquivo):

&nbsp;   if not os.path.exists(nome\_arquivo):

&nbsp;       pd.DataFrame().to\_csv(nome\_arquivo, index=False)

&nbsp;   return pd.read\_csv(nome\_arquivo)



def salvar\_csv(df, nome\_arquivo):

&nbsp;   df.to\_csv(nome\_arquivo, index=False)



\# ------------------------------------------------------------

\# 🔍 Carregando bases

\# ------------------------------------------------------------

ambientes\_df = carregar\_csv("base\_ambientes.csv")

caixas\_df = carregar\_csv("base\_caixas.csv")

clientes\_df = carregar\_csv("clientes.csv")

projetos\_df = carregar\_csv("projetos.csv")



\# ------------------------------------------------------------

\# 🧮 Seção principal – cálculo

\# ------------------------------------------------------------

st.header("📊 Novo Projeto")



\# Cliente

st.subheader("Cliente")

clientes = clientes\_df\["Nome"].tolist()

cliente\_sel = st.selectbox("Selecione o cliente", clientes)

if st.button("➕ Novo Cliente"):

&nbsp;   with st.form("novo\_cliente"):

&nbsp;       nome = st.text\_input("Nome do Cliente")

&nbsp;       contato = st.text\_input("Contato (telefone/email)")

&nbsp;       endereco = st.text\_input("Endereço")

&nbsp;       cidade = st.text\_input("Cidade")

&nbsp;       estado = st.text\_input("Estado")

&nbsp;       enviar = st.form\_submit\_button("Salvar")

&nbsp;       if enviar:

&nbsp;           novo\_id = f"C{len(clientes\_df)+1:03d}"

&nbsp;           clientes\_df.loc\[len(clientes\_df)] = \[novo\_id,nome,contato,endereco,cidade,estado]

&nbsp;           salvar\_csv(clientes\_df,"clientes.csv")

&nbsp;           st.success("Cliente salvo!")



\# Ambiente

st.subheader("Ambiente")

ambiente\_sel = st.selectbox("Selecione o tipo de ambiente", ambientes\_df\["Nome"])

if st.button("➕ Novo Ambiente"):

&nbsp;   with st.form("novo\_ambiente"):

&nbsp;       nome = st.text\_input("Nome do Ambiente")

&nbsp;       spl = st.number\_input("SPL alvo (dB)",60,110,85)

&nbsp;       rt60 = st.number\_input("RT60 alvo (s)",0.2,3.0,1.0,step=0.1)

&nbsp;       abs\_m = st.number\_input("Coeficiente médio de absorção",0.1,1.0,0.3,step=0.05)

&nbsp;       cob = st.number\_input("Cobertura padrão (m²)",10,200,40)

&nbsp;       enviar = st.form\_submit\_button("Salvar")

&nbsp;       if enviar:

&nbsp;           ambientes\_df.loc\[len(ambientes\_df)] = \[nome,spl,rt60,abs\_m,cob]

&nbsp;           salvar\_csv(ambientes\_df,"base\_ambientes.csv")

&nbsp;           st.success("Ambiente adicionado!")



\# Caixa

st.subheader("Equipamento")

caixa\_sel = st.selectbox("Selecione o modelo de caixa", caixas\_df\["Modelo"])

if st.button("➕ Nova Caixa"):

&nbsp;   with st.form("nova\_caixa"):

&nbsp;       marca = st.text\_input("Marca")

&nbsp;       modelo = st.text\_input("Modelo")

&nbsp;       tipo = st.text\_input("Tipo (ativa/passiva, tamanho)")

&nbsp;       sens = st.number\_input("Sensibilidade (dB/W/m)",80,110,95)

&nbsp;       pot = st.number\_input("Potência RMS (W)",50,5000,300)

&nbsp;       cob = st.number\_input("Cobertura (m²)",5,200,35)

&nbsp;       enviar = st.form\_submit\_button("Salvar")

&nbsp;       if enviar:

&nbsp;           caixas\_df.loc\[len(caixas\_df)] = \[marca,modelo,tipo,sens,pot,cob]

&nbsp;           salvar\_csv(caixas\_df,"base\_caixas.csv")

&nbsp;           st.success("Caixa adicionada!")



\# Parâmetros geométricos

st.subheader("Dimensões do ambiente")

col1, col2, col3 = st.columns(3)

compr = col1.number\_input("Comprimento (m)",5.0,100.0,20.0)

larg = col2.number\_input("Largura (m)",5.0,100.0,10.0)

alt = col3.number\_input("Pé-direito (m)",2.0,10.0,3.0)



area = compr \* larg

volume = area \* alt



\# Dados selecionados

amb\_data = ambientes\_df.loc\[ambientes\_df\["Nome"]==ambiente\_sel].iloc\[0]

cx\_data = caixas\_df.loc\[caixas\_df\["Modelo"]==caixa\_sel].iloc\[0]



\# Cálculo SPL e potência

spl\_desejado = amb\_data\["SPL\_alvo"]

dist\_media = compr/2

perda = 20\*np.log10(dist\_media)

spl\_ajust = cx\_data\["Sensibilidade"] + 10\*np.log10(cx\_data\["Potencia\_RMS"]) - perda

dif\_db = max(spl\_desejado - spl\_ajust, 0)

pot\_necessaria = cx\_data\["Potencia\_RMS"] \* (2\*\*(dif\_db/3))

num\_caixas = math.ceil(area / cx\_data\["Cobertura\_m2"])

pot\_total = pot\_necessaria \* num\_caixas



\# RT60

alpha = amb\_data\["Absorcao\_media"]

rt60 = 0.161 \* (volume / (area \* alpha))

if rt60 > 1.5: classe = "🟨 Reverberação Alta"

elif rt60 < 0.4: classe = "🟦 Ambiente Seco"

else: classe = "🟩 Acústica Adequada"



\# ------------------------------------------------------------

\# 🧾 Resultados

\# ------------------------------------------------------------

st.markdown("---")

st.header("📈 Resultados")



if modo\_completo:

&nbsp;   st.metric("Área (m²)", f"{area:.1f}")

&nbsp;   st.metric("Volume (m³)", f"{volume:.1f}")

&nbsp;   st.metric("Perda sonora (dB)", f"{perda:.1f}")



col1, col2 = st.columns(2)

col1.metric("SPL ajustado", f"{spl\_ajust:.1f} dB")

col1.metric("Caixas necessárias", int(num\_caixas))

col2.metric("Potência total", f"{pot\_total:.0f} W")

col2.metric("RT60", f"{rt60:.2f} s")



st.success(f"Classificação: {classe}")



\# ------------------------------------------------------------

\# 💾 Salvamento do projeto

\# ------------------------------------------------------------

if st.button("💾 Salvar Projeto"):

&nbsp;   cliente\_id = clientes\_df.loc\[clientes\_df\["Nome"]==cliente\_sel, "Cliente\_ID"].values\[0]

&nbsp;   proj\_id = f"P{len(projetos\_df)+1:03d}"

&nbsp;   novos\_dados = \[proj\_id,cliente\_id,ambiente\_sel,cx\_data\["Modelo"],spl\_desejado,spl\_ajust,

&nbsp;                  pot\_total,rt60,classe,datetime.now().strftime("%Y-%m-%d")]

&nbsp;   projetos\_df.loc\[len(projetos\_df)] = novos\_dados

&nbsp;   salvar\_csv(projetos\_df,"projetos.csv")

&nbsp;   st.success("Projeto salvo com sucesso!")



\# ------------------------------------------------------------

\# 📂 Projetos existentes

\# ------------------------------------------------------------

st.markdown("---")

st.header("📁 Projetos Salvos")

if not projetos\_df.empty:

&nbsp;   st.dataframe(projetos\_df\[\["Projeto\_ID","Ambiente","Caixa","Classificacao","Data"]])

else:

&nbsp;   st.info("Nenhum projeto salvo ainda.")



