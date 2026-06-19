import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# =====================================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================================
st.set_page_config(page_title="Zion Tecnologia - Gestão Portuária", page_icon="🚢", layout="wide")

# =====================================================================
# BLOCO: ESTILIZAÇÃO VISUAL (CSS DE ALTO CONTRASTE + MENU LATERAL PRETO)
# =====================================================================
def aplicar_estilo_visual():
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        }
        
        /* Textos comuns em Verde Neon */
        p, label, .stText, p code, .stMarkdown p {
            color: #00ff66 !important;
            font-weight: bold !important;
            font-size: 16px !important;
        }
        
        /* Inputs do Formulário */
        .stTextInput input, .stNumberInput input, .stSelectbox div {
            color: #00ff66 !important;
            font-weight: bold !important;
            background-color: #1e293b !important;
        }
        
        /* Métricas */
        [data-testid="stMetricValue"] {
            color: #00ff66 !important;
            font-weight: bold !important;
            font-size: 32px !important;
        }
        [data-testid="stMetricLabel"] p {
            color: #38bdf8 !important;
        }
        
        /* Estilização de Cabeçalhos e Tabelas */
        th {
            color: #38bdf8 !important;
            font-size: 16px !important;
            font-weight: bold !important;
            text-align: left;
        }
        td {
            color: #00ff66 !important;
            font-size: 15px !important;
            font-weight: bold !important;
        }
        
        /* ESTILO DOS BOTÕES DE NAVEGAÇÃO LATERAL (COR PRETA) */
        .stSidebar div.stButton > button {
            background-color: #000000 !important;
            color: #00ff66 !important;
            border: 2px solid #00ff66 !important;
            font-weight: bold !important;
            font-size: 15px !important;
            transition: all 0.3s ease;
            margin-bottom: 10px;
        }
        .stSidebar div.stButton > button:hover {
            background-color: #00ff66 !important;
            color: #000000 !important;
            border: 2px solid #000000 !important;
        }
        
        .custom-box {
            background-color: rgba(15, 23, 42, 0.8);
            padding: 1.5rem;
            border-radius: 12px;
            border: 2px solid #00ff66;
            margin-bottom: 1rem;
        }
        h1, h2, h3, h4, h5, h6 { 
            color: #38bdf8 !important; 
            font-weight: bold !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# =====================================================================
# BLOCO: BANCO DE DADOS EM MEMÓRIA COM PERMISSÕES DEFINIDAS
# =====================================================================
def inicializar_dados():
    if 'banco_usuarios' not in st.session_state:
        st.session_state.banco_usuarios = {
            "admin": {"senha": "1234", "role": "admin"},
            "admin2": {"senha": "5678", "role": "admin"},
            "alex": {"senha": "zion2026", "turno_fixo": "1º TURNO", "role": "operador"}
        }
    
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'user_name' not in st.session_state: st.session_state.user_name = ""
    if 'turno_trabalho' not in st.session_state: st.session_state.turno_trabalho = "1º TURNO"
    if 'role' not in st.session_state: st.session_state.role = "operador"
    if 'menu_atual' not in st.session_state: st.session_state.menu_atual = "Lançamentos"

    colunas = ["Dia", "Porão 1", "Porão 2", "Porão 3", "Porão 4", "Saldo"]
    if 'tabela_turno_1' not in st.session_state:
        st.session_state.tabela_turno_1 = pd.DataFrame(columns=colunas)
    if '
