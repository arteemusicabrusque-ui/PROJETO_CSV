import streamlit as st
import pandas as pd
from datetime import datetime
import io
from fpdf import FPDF

# ======================================================
# CONFIGURAÇÕES INICIAIS
# ======================================================

st.set_page_config(
    page_title="AcousticCalc Web – PROJETO_CSV",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Tema escuro
st.markdown(
    """
    <style>
        body {background-color: #121212; color: #f5f5f5;}
        .stButton>button {
            background-color: #d32f2f;
            color: white;
            border-radius: 8px;
            border: none;
            font-weight: bold;
        }
        .stTextInput>div>div>input, .stSelectbox>div>div>select {
            background-color: #1e1e1e;
            color: #e0e0e0;
            border: 1px solid #444;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ======================================================
# FUNÇÕES DE SUPORTE
# ======================================================

def carregar_csv(nome_arquivo):
    try:
        return pd.read_csv(nome_arquivo, encoding="utf-8", sep=",")
    except Exception:
        return pd.DataFrame()

def salvar_csv(df, nome_arquivo):
    df.to_csv(nome_arquivo, index=False, encoding="utf-8")

def calcular_potencia(area, pe_direito, spl_desejado, sensibilidade):
    fator_area = area / 100
    fator_altura = 1 + ((pe_direito - 3) * 0.05)
    potencia_w = 10 ** ((spl_desejado - sensibilidade) / 10) * fator_area * fator_altura
    return round(potencia_w, 2)

def gerar_pdf(cliente, ambiente, caixa, potencia, spl, orcamento, logo=None, empresa="Arte & Música Sonorização de Ambientes"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, f"{empresa} - Relatório Técnico", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.ln(10)
    pdf.cell(200, 8, f"Cliente: {cliente}", ln=True)
    pdf.cell(200, 8, f"Ambiente: {ambiente}", ln=True)
    pdf.cell(200, 8, f"Caixa acústica: {caixa}", ln=True)
    pdf.cell(200, 8, f"Potência calculada: {potencia} W", ln=True)
    pdf.cell(200, 8, f"Nível estimado: {spl} dB SPL", ln=True)
    pdf.cell(200, 8, f"Orçamento estimado: R$ {orcamento}", ln=True)
    pdf.cell(200, 8, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# ======================================================
# CARREGAR BASES
# ======================================================

clientes_df = carregar_csv("clientes.csv")
ambientes_df = carregar_csv("base_ambientes.csv")
caixas_df = carregar_csv("base_caixas.csv")
projetos_df = carregar_csv("projetos.csv")

# ======================================================
# INTERFACE
# ======================================================

st.title("🎶 AcousticCalc Web – Sistema de Cálculo e Dimensionamento")
st.write("Versão prática e comercial – Tema escuro")

modo = st.toggle("💡 Modo completo / resumido", value=True)

abas = st.tabs(["Clientes", "Ambientes", "Caixas", "Cálculo & Relatório", "Configurações"])

# ======================================================
# ABA CLIENTES
# ======================================================
with abas[0]:
    st.header("👤 Cadastro de Clientes")
    with st.form("novo_cliente"):
        nome = st.text_input("Nome do Cliente")
        tel = st.text_input("Telefone")
        email = st.text_input("Email")
        end = st.text_input("Endereço")
        obs = st.text_area("Observações")
        if st.form_submit_button("Salvar Cliente"):
            novo = pd.DataFrame([[nome, tel, email, end, obs]],
                                columns=["Nome", "Telefone", "Email", "Endereco", "Observacoes"])
            clientes_df = pd.concat([clientes_df, novo], ignore_index=True)
            salvar_csv(clientes_df, "clientes.csv")
            st.success("Cliente salvo com sucesso!")

    st.dataframe(clientes_df)

# ======================================================
# ABA AMBIENTES
# ======================================================
with abas[1]:
    st.header("🏢 Cadastro de Ambientes")
    with st.form("novo_ambiente"):
        nome = st.text_input("Nome do Ambiente")
        tipo = st.selectbox("Tipo de ambiente", [
            "Restaurante", "Bar", "Academia", "Shopping", "Igreja",
            "Auditório", "Show", "Home Theater", "Consultório", "Sala Comercial"
        ])
        area = st.number_input("Área (m²)", min_value=10.0)
        altura = st.number_input("Pé-direito (m)", min_value=2.0)
        rev = st.selectbox("Reverberação", ["Baixa", "Média", "Alta"])
        obs = st.text_area("Observações")
        if st.form_submit_button("Salvar Ambiente"):
            novo = pd.DataFrame([[nome, tipo, area, altura, rev, obs]],
                                columns=["Nome", "Tipo", "Area_m2", "Pe_Direito_m", "Reverberacao", "Observacoes"])
            ambientes_df = pd.concat([ambientes_df, novo], ignore_index=True)
            salvar_csv(ambientes_df, "base_ambientes.csv")
            st.success("Ambiente salvo!")

    st.dataframe(ambientes_df)

# ======================================================
# ABA CAIXAS
# ======================================================
with abas[2]:
    st.header("🔊 Cadastro de Caixas Acústicas")
    with st.form("nova_caixa"):
        nome = st.text_input("Modelo")
        tipo = st.selectbox("Tipo", ["Full Range", "Subwoofer", "Line Array", "Tweeter", "Mid-Range"])
        sens = st.number_input("Sensibilidade (dB)", 80, 110, 90)
        pot = st.number_input("Potência RMS (W)", 10, 5000, 100)
        splmax = st.number_input("SPL Máximo (dB)", 90, 140, 120)
        freq = st.text_input("Resposta de Frequência", "50Hz – 18kHz")
        imp = st.number_input("Impedância (Ohms)", 2, 16, 8)
        if st.form_submit_button("Salvar Caixa"):
            novo = pd.DataFrame([[nome, tipo, sens, pot, splmax, freq, imp]],
                                columns=["Nome", "Tipo", "Sensibilidade_dB", "Potencia_W", "SPL_Max_dB", "Freq_Resposta", "Impedancia_Ohms"])
            caixas_df = pd.concat([caixas_df, novo], ignore_index=True)
            salvar_csv(caixas_df, "base_caixas.csv")
            st.success("Caixa salva!")

    st.dataframe(caixas_df)

# ======================================================
# ABA CÁLCULO & RELATÓRIO
# ======================================================
with abas[3]:
    st.header("📊 Cálculo e Relatório Técnico")

    cliente = st.selectbox("Cliente", clientes_df["Nome"].unique() if not clientes_df.empty else [])
    ambiente = st.selectbox("Ambiente", ambientes_df["Nome"].unique() if not ambientes_df.empty else [])

    if "Nome" in caixas_df.columns:
    caixa = st.selectbox("Caixa", caixas_df["Nome"].unique())
else:
    st.warning("A coluna 'Nome' não foi encontrada em base_caixas.csv")
    caixa = None


    if ambiente and caixa:
        amb_info = ambientes_df[ambientes_df["Nome"] == ambiente].iloc[0]
        caixa_info = caixas_df[caixas_df["Nome"] == caixa].iloc[0]
        tipo = amb_info["Tipo"]
        area = amb_info["Area_m2"]
        altura = amb_info["Pe_Direito_m"]
        sens = caixa_info["Sensibilidade_dB"]

        # Tabela SPL padrão
        spl_table = {
            "Restaurante": 80, "Bar": 85, "Academia": 90, "Shopping": 75, "Igreja": 88,
            "Auditório": 85, "Show": 100, "Home Theater": 95, "Consultório": 70, "Sala Comercial": 68
        }
        spl_desejado = spl_table.get(tipo, 85)
        potencia = calcular_potencia(area, altura, spl_desejado, sens)
        orcamento = round(potencia * 1.5, 2)

        st.subheader("🔧 Resultado do cálculo")
        st.write(f"**SPL desejado:** {spl_desejado} dB")
        st.write(f"**Potência estimada:** {potencia} W RMS")
        st.write(f"**Orçamento sugerido:** R$ {orcamento}")

        if st.button("📄 Baixar relatório técnico (PDF)"):
            buffer = gerar_pdf(cliente, ambiente, caixa, potencia, spl_desejado, orcamento)
            st.download_button("⬇️ Download PDF", data=buffer, file_name="relatorio_acustico.pdf")

# ======================================================
# ABA CONFIGURAÇÕES
# ======================================================
with abas[4]:
    st.header("⚙️ Configurações")
    empresa = st.text_input("Nome da empresa", "Arte & Música Sonorização de Ambientes")
    st.file_uploader("Logo da empresa (PNG/JPG)", type=["png", "jpg", "jpeg"])
    st.info("Essas informações serão aplicadas nos relatórios futuros.")

