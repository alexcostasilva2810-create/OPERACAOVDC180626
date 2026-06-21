import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA E ESTILIZAÇÃO COMPLETA (PRETO E VERDE CLARO)
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Zion Operações", layout="wide")

st.markdown(
    """
    <style>
    .stApp, [data-testid="stSidebar"], div[data-testid="stExpander"] {
        background-color: #000000 !important;
    }
    h1, h2, h3, p, label, .stMarkdown, [data-testid="stMetricLabel"], [data-testid="stMetricValue"] {
        color: #00FF66 !important;
    }
    .stButton>button {
        background-color: #000000 !important;
        color: #00FF66 !important;
        border: 2px solid #00FF66 !important;
        border-radius: 5px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #00FF66 !important;
        color: #000000 !important;
    }
    input, select, div[data-baseweb="select"] {
        background-color: #000000 !important;
        color: #00FF66 !important;
        border: 1px solid #00FF66 !important;
    }
    .stDataFrame, div[data-testid="stTable"] {
        background-color: #000000 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------------------------------------------------------
# URL DO SEU GOOGLE APPS SCRIPT ATUALIZADA
# -----------------------------------------------------------------------------
URL_WEB_APP = "https://script.google.com/macros/s/AKfycbxy_cHemynJwqmOwtIoZBJg8GwXKvPYv-qlYHLvCkblW6xcOWPq8yMINvQITkgRnolN/exec"

# -----------------------------------------------------------------------------
# BANCO DE USUÁRIOS
# -----------------------------------------------------------------------------
LISTA_USUARIOS = {
    "Denilson": {"senha": "9607", "cargo": "visualizador_global", "turno": "Todos"},
    "Fabio": {"senha": "7777", "cargo": "visualizador_global", "turno": "Todos"},
    "Alex": {"senha": "1234", "cargo": "admin", "turno": "Todos"},
    "Rubens Ferreira": {"senha": "8036", "cargo": "operador", "turno": "2º TURNO"},
    "Tallison Menezes": {"senha": "4991", "cargo": "operador", "turno": "1º TURNO"},
    "Caio Rosario": {"senha": "6244", "cargo": "operador", "turno": "1º TURNO"},
    "Cleyvson Cardoso": {"senha": "4194", "cargo": "operador", "turno": "2º TURNO"},
}

st.session_state.usuarios_db = LISTA_USUARIOS

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "usuario_atual" not in st.session_state:
    st.session_state.usuario_atual = ""

if "cargo_atual" not in st.session_state:
    st.session_state.cargo_atual = ""

if "menu_atual" not in st.session_state:
    st.session_state.menu_atual = "Lançamentos do Turno"

REFERENCIA_CONTRATUAL = 50000.0
COLUNAS_PADRAO = ["Turno", "Dia", "Porão 1", "Porão 2", "Porão 3", "Porão 4", "Porão 5", "Saldo", "Usuário", "Hora do Registro"]

# -----------------------------------------------------------------------------
# FUNÇÕES DE COMUNICAÇÃO DIRETAS VIA API DO GOOGLE
# -----------------------------------------------------------------------------
def tratar_formato_hora(hora_bruta):
    try:
        hora_str = str(hora_bruta).strip()
        if "T" in hora_str:
            tempo_limpo = hora_str.split("T")[1].split(".")[0]
            return tempo_limpo
        return hora_str
    except Exception:
        return hora_bruta

def carregar_dados_nuvem():
    try:
        response = requests.get(URL_WEB_APP, timeout=10)
        if response.status_code == 200:
            dados = response.json()
            if not dados:
                return pd.DataFrame(columns=COLUNAS_PADRAO)
            df = pd.DataFrame(dados)
            
            colunas_numericas = ["Porão 1", "Porão 2", "Porão 3", "Porão 4", "Porão 5", "Saldo"]
            for col in colunas_numericas:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
            
            if "Hora do Registro" in df.columns:
                df["Hora do Registro"] = df["Hora do Registro"].apply(tratar_formato_hora)
            
            return df[[c for c in COLUNAS_PADRAO if c in df.columns]]
    except Exception:
        pass
    return pd.DataFrame(columns=COLUNAS_PADRAO)

def atualizar_planilha_nuvem(df_novo):
    try:
        dados_json = df_novo.to_dict(orient="records")
        response = requests.post(URL_WEB_APP, json=dados_json, timeout=15)
        # Ajuste para aceitar qualquer retorno bem-sucedido (200) do script do Google
        if response.status_code == 200:
            return True
    except Exception:
        pass
    return False

if "dados_operacao" not in st.session_state:
    st.session_state.dados_operacao = carregar_dados_nuvem()

# -----------------------------------------------------------------------------
# TELA DE LOGIN
# -----------------------------------------------------------------------------
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; font-size: 50px;'>ZION</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-weight: bold; font-size: 14px; margin-top: -20px; letter-spacing: 4px;'>TECNOLOGIA PORTUÁRIA</p>", unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        st.markdown(
            """
            <div style='border: 2px solid #00FF66; padding: 25px; border-radius: 10px; margin-top: 20px;'>
                <h3 style='text-align: center; margin-top: 0px;'>Login de Acesso</h3>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        user_input = st.text_input("Nome de Usuário", key="login_user")
        pass_input = st.text_input("Senha", type="password", key="login_pass")
        
        if st.button("Entrar no Sistema", use_container_width=True):
            db = st.session_state.usuarios_db
            if user_input in db and str(db[user_input]["senha"]) == str(pass_input):
                st.session_state.logged_in = True
                st.session_state.usuario_atual = user_input
                st.session_state.cargo_atual = db[user_input]["cargo"]
                
                if st.session_state.cargo_atual == "visualizador_global":
                    st.session_state.menu_atual = "Global (Consolidado)"
                else:
                    st.session_state.menu_atual = "Lançamentos do Turno"
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")

# -----------------------------------------------------------------------------
# INTERFACE LOGADA
# -----------------------------------------------------------------------------
else:
    df_atual = st.session_state.dados_operacao

    st.sidebar.title("Zion Operações")
    st.sidebar.write(f"🟢 **Usuário:** {st.session_state.usuario_atual}")
    
    if st.sidebar.button("Atualizar Dados Nuvem", use_container_width=True):
        st.session_state.dados_operacao = carregar_dados_nuvem()
        st.rerun()
    
    if st.session_state.cargo_atual != "visualizador_global":
        if st.sidebar.button("Lançamentos do Turno", use_container_width=True):
            st.session_state.menu_atual = "Lançamentos do Turno"
            
        if st.session_state.cargo_atual == "admin":
            if st.sidebar.button("Global (Consolidado)", use_container_width=True):
                st.session_state.menu_atual = "Global (Consolidado)"
    else:
        st.sidebar.write("📌 *Acesso restrito ao Painel Global*")
        
    if st.sidebar.button("Sair", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.usuario_atual = ""
        st.session_state.cargo_atual = ""
        st.rerun()

    st.sidebar.markdown("---")
    
    user_info = st.
