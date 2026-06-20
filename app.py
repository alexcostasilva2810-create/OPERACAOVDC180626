import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from streamlit_gsheets import GSheetsConnection

# Configuração da página
st.set_page_config(page_title="Zion Tecnologia - Gestão Portuária", page_icon="🚢", layout="wide")

# 1. INICIALIZAÇÃO DO BANCO DE USUÁRIOS
if 'banco_usuarios' not in st.session_state:
    st.session_state.banco_usuarios = {
        "admin": {"senha": "1234", "role": "admin"},
        "admin2": {"senha": "5678", "role": "admin"},
        "alex": {"senha": "zion2026", "turno_fixo": "1º TURNO", "role": "operador"},
        "Rubens Ferreira": {"senha": "8036", "turno_fixo": "2º TURNO", "role": "operador"}
    }

# FUNÇÃO PARA PEGAR A HORA ATUAL DO BRASIL
def obter_hora_atual_brasil():
    hora_local = datetime.utcnow() - timedelta(hours=3)
    return hora_local.strftime("%H:%M:%S")

# 2. ESTILIZAÇÃO CSS COMPLETA (SEM O RETÂNGULO VAZIO NO LOGIN)
st.markdown(
    """
    <style>
    /* TODO O SISTEMA: Fundo preto */
    .stApp, [data-testid="stSidebar"] { 
        background-color: #000000 !important; 
    }
    
    /* Textos do sistema em verde */
    p, label, .stMarkdown p, .stSelectbox label, .stInputField label, .stDateInput label { 
        color: #00ff66 !important; 
        font-weight: bold !important; 
    }
    h1, h2, h3, h4 { color: #00ff66 !important; font-weight: bold !important; }
    
    /* Título ZION Elegante no Topo */
    .zion-header {
        text-align: center;
        font-family: 'Helvetica Neue', sans-serif;
        font-size: 55px;
        font-weight: 900;
        letter-spacing: 10px;
        color: #00ff66;
        margin-top: 3rem;
        margin-bottom: 0px;
    }
    
    .zion-subtitle {
        text-align: center;
        font-size: 13px;
        letter-spacing: 4px;
        color: #00ff66;
        margin-top: 0px;
        margin-bottom: 2.5rem;
        text-transform: uppercase;
        opacity: 0.8;
    }

    /* Container customizado do Login */
    .login-container {
        border: 2px solid #00ff66;
        border-radius: 12px;
        padding: 25px;
        background-color: #000000;
    }

    /* Letras de todos os botões do menu lateral em PRETO */
    [data-testid="stSidebar"] button p {
        color: #000000 !important;
        font-weight: bold !important;
    }
    
    /* Estilo do botão de navegação lateral (Fundo Branco) */
    [data-testid="stSidebar"] button {
        background-color: #ffffff !important;
        border: 1px solid #00ff66 !important;
    }

    /* Tabelas e Editores (Fundo branco, letras pretas e CENTRALIZADO) */
    .tabela-global-exclusiva td, .tabela-global-exclusiva th, .tabela-global-exclusiva p, .tabela-global-exclusiva span {
        color: #000000 !important;
        font-weight: normal !important;
        text-align: center !important;
    }
    [data-testid="stTable"] td, [data-testid="stDataFrame"] td, [data-testid="stDataEditor"] td {
        text-align: center !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'turno_trabalho' not in st.session_state: st.session_state.turno_trabalho = "1º TURNO"
if 'role' not in st.session_state: st.session_state.role = "operador"
if 'menu_atual' not in st.session_state: st.session_state.menu_atual = "Lançamentos"

colunas = ["Dia", "Porão 1", "Porão 2", "Porão 3", "Porão 4", "Porão 5", "Saldo", "Usuario", "Hora"]
if 'tabela_turno_1' not in st.session_state: st.session_state.tabela_turno_1 = pd.DataFrame(columns=colunas)
if 'tabela_turno_2' not in st.session_state: st.session_state.tabela_turno_2 = pd.DataFrame(columns=colunas)
if 'edit_mode' not in st.session_state: st.session_state.edit_mode = False
if 'edit_index' not in st.session_state: st.session_state.edit_index = None

def sincronizar_visao_global_com_sheets(df_global_atual):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_salvar = df_global_atual.copy()
        df_salvar.columns = ["Turno", "Dia", "Porão 1", "Porão 2", "Porão 3", "Porão 4", "Porão 5", "Saldo", "Usuário", "Hora do Registro"]
        conn.update(worksheet="Global", data=df_salvar)
        st.cache_data.clear()
    except Exception as e:
        pass

def obter_df_combinado():
    df1 = st.session_state.tabela_turno_1.copy()
    df1["Turno"] = "1º TURNO"
    df1["orig_index"] = df1.index
    
    df2 = st.session_state.tabela_turno_2.copy()
    df2["Turno"] = "2º TURNO"
    df2["orig_index"] = df2.index
    
    df_combinado = pd.concat([df1, df2], ignore_index=True)
    ordem_colunas = ["Turno", "Dia", "Porão 1", "Porão 2", "Porão 3", "Porão 4", "Porão 5", "Saldo", "Usuario", "Hora", "orig_index"]
    if not df_combinado.empty:
        return df_combinado[ordem_colunas]
    return pd.DataFrame(columns=ordem_colunas)

def gerar_pdf_reportlab(p1, p2, p3, p4, p5, saldo, df_combinado):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=20, leftMargin=20, topMargin=40, bottomMargin=40)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('T1', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#0f172a'), alignment=1, spaceAfter=15)
    normal_style = ParagraphStyle('N', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#1e293b'))

    story.append(Paragraph("Relatório Consolidado de Carregamento - Global", title_style))
    story.append(Paragraph("<b>Zion Tecnologia</b> — Sistema de Controle Portuário", normal
