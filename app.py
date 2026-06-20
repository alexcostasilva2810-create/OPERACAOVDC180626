import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Zion Tecnologia - Gestão Portuária", page_icon="🚢", layout="wide")

conn = st.connection("gsheets", type=GSheetsConnection)

if 'banco_usuarios' not in st.session_state:
    st.session_state.banco_usuarios = {
        "admin": {"senha": "1234", "role": "admin"},
        "admin2": {"senha": "5678", "role": "admin"},
        "alex": {"senha": "zion2026", "turno_fixo": "1º TURNO", "role": "operador"},
        "Rubens Ferreira": {"senha": "8036", "turno_fixo": "2º TURNO", "role": "operador"}
    }

def carregar_dados_sheets():
    try:
        df = conn.read(worksheet="Global", ttl=0)
        if df.empty:
            return pd.DataFrame(columns=["Turno", "Dia", "Porão 1", "Porão 2", "Porão 3", "Porão 4", "Porão 5", "Saldo", "Usuário", "Hora do Registro"])
        return df
    except Exception:
        return pd.DataFrame(columns=["Turno", "Dia", "Porão 1", "Porão 2", "Porão 3", "Porão 4", "Porão 5", "Saldo", "Usuário", "Hora do Registro"])

def salvar_dados_sheets(df):
    try:
        st.cache_data.clear()
        conn.update(worksheet="Global", data=df)
    except Exception as e:
        st.error(f"Erro crítico na gravação do Sheets: {e}")

def obter_hora_atual_brasil():
    return (datetime.utcnow() - timedelta(hours=3)).strftime("%H:%M:%S")

st.markdown(
    """
    <style>
    .stApp, [data-testid="stSidebar"] { background-color: #000000 !important; }
    p, label, .stMarkdown p, .stSelectbox label, .stInputField label, .stDateInput label { color: #00ff66 !important; font-weight: bold !important; }
    h1, h2, h3, h4 { color: #00ff66 !important; font-weight: bold !important; }
    .zion-header { text-align: center; font-family: 'Helvetica Neue', sans-serif; font-size: 55px; font-weight: 900; letter-spacing: 10px; color: #00ff66; margin-top: 3rem; margin-bottom: 0px; }
    .zion-subtitle { text-align: center; font-size: 13px; letter-spacing: 4px; color: #00ff66; margin-top: 0px; margin-bottom: 2.5rem; text-transform: uppercase; opacity: 0.8; }
    .login-container { border: 2px solid #00ff66; border-radius: 12px; padding: 25px; background-color: #000000; }
    [data-testid="stSidebar"] button p { color: #000000 !important; font-weight: bold !important; }
    [data-testid="stSidebar"] button { background-color: #ffffff !important; border: 1px solid #00ff66 !important; }
    .tabela-global-exclusiva td, .tabela-global-exclusiva th, .tabela-global-exclusiva p, .tabela-global-exclusiva span { color: #000000 !important; font-weight: normal !important; text-align: center !important; }
    [data-testid="stTable"] td, [data-testid="stDataFrame"] td, [data-testid="stDataEditor"] td { text-align: center !important; }
    </style>
    """,
    unsafe_allow_html=True
)

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'turno_trabalho' not in st.session_state: st.session_state.turno_trabalho = "1º TURNO"
if 'role' not in st.session_state: st.session_state.role = "operador"
if 'menu_atual' not in st.session_state: st.session_state.menu_atual = "Lançamentos"
if 'edit_mode' not in st.session_state: st.session_state.edit_mode = False
if 'edit_index' not in st.session_state: st.session_state.edit_index = None

def bloco_consolidado_geral():
    st.markdown("<h2 style='text-align: center;'>Painel Gerencial Global (5 Porões)</h2>", unsafe_allow_html=True)
    df_global = carregar_dados_sheets()
    
    p1 = pd.to_numeric(df_global["Porão 1"], errors='coerce').fillna(0).sum() if not df_global.empty else 0
    p2 = pd.to_numeric(df_global["Porão 2"], errors='coerce').fillna(0).sum() if not df_global.empty else 0
    p3 = pd.to_numeric(df_global["Porão 3"], errors='coerce').fillna(0).sum() if not df_global.empty else 0
    p4 = pd.to_numeric(df_global["Porão 4"], errors='coerce').fillna(0).sum() if not df_global.empty else 0
    p5 = pd.to_numeric(df_global["Porão 5"], errors='coerce').fillna(0).sum() if not df_global.empty else 0
        
    saldo_geral = p1 + p2 + p3 + p4 + p5
    meta_referencia = 50000
    falta_atingir = max(0, meta_referencia - saldo_geral)

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total Porão 1", f"{int(p1)} t")
    c2.metric("Total Porão 2", f"{int(p2)} t")
    c3.metric("Total Porão 3", f"{int(p3)} t")
    c4.metric("Total Porão 4", f"{int(p4)} t")
    c5.metric("Total Porão 5", f"{int(p5)} t")
    c6.metric("TOTAL JÁ LANÇADO", f"{int(saldo_geral)} t")

    st.markdown("---")
    if not df_global.empty:
        st.markdown('<div class="tabela-global-exclusiva">', unsafe_allow_html=True)
        linhas_editadas = st.data_editor(df_global.style.set_properties(**{'text-align': 'center'}), use_container_width=True, hide_index=True, num_rows="dynamic")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if len(linhas_editadas) < len(df_global):
            salvar_dados_sheets(df_global.iloc[linhas_editadas.index.tolist()].reset_index(drop=True))
            st.rerun()

def bloco_painel_poroes(turno_atual):
    st.markdown(f"<h2>Lançamentos Atuais - {turno_atual}</h2>", unsafe_allow_html=True)
    df_global = carregar_dados_sheets()
    
    # Previne que erros de colunas vazias travem o filtro
    if "Turno" in df_global.columns:
        df_atual = df_global[df_global["Turno"] == turno_atual].reset_index(drop=True)
    else:
        df_atual = pd.DataFrame()

    with st.expander("Novo Lançamento (5 Porões)", expanded=True):
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1: data_lan = st.date_input("Data", format="DD/MM/YYYY")
        with col2: v1 = st.number_input("Porão 1 (t)", min_value=0, step=50, value=0)
        with col3: v2 = st.number_input("Porão 2 (t)", min_value=0, step=50, value=0)
        with col4: v3 = st.number_input("Porão 3 (t)", min_value=0, step=50, value=0)
        with col5: v4 = st.number_input("Porão 4 (t)", min_value=0, step=50, value=0)
        with col6: v5 = st.number_input("Porão 5 (t)", min_value=0, step=50, value=0)
        
        if st.button("Gravar Lançamento", use_container_width=True):
            novo_registro = pd.DataFrame([{
                "Turno": turno_atual, "Dia": data_lan.strftime("%d/%m/%Y"),
                "Porão 1": v1, "Porão 2": v2, "Porão 3": v3, "Porão 4": v4, "Porão 5": v5,
                "Saldo": v1+v2+v3+v4+v5, "Usuário": st.session_state.user_name, "Hora do Registro": obter_hora_atual_brasil()
            }])
            df_atualizado = pd.concat([df_global, novo_registro], ignore_index=True)
            salvar_dados_sheets(df_atualizado)
            st.rerun()

    if not df_atual.empty:
        st.dataframe(df_atual.drop(columns=["Turno", "Usuário", "Hora do Registro"], errors='ignore'), use_container_width=True, hide_index=True)

def bloco_login():
    st.markdown('<div class="zion-header">ZION</div>', unsafe_allow_html=True)
    st.markdown('<div class="zion-subtitle">Tecnologia Portuária</div>', unsafe_allow_html=True)
    _, col_centro, _ = st.columns([1.5, 1.2, 1.5])
    with col_centro:
        st.markdown('<div class="login-container"><h4 style="text-align: center; margin-bottom: 20px; color: #00ff66;">Login de Acesso</h4>', unsafe_allow_html=True)
        u = st.text_input("Nome de Usuário", placeholder="Digite seu usuário")
        p = st.text_input("Senha", type="password", placeholder="Digite sua senha")
        if st.button("Entrar no Sistema", use_container_width=True):
            if u in st.session_state.banco_usuarios and st.session_state.banco_usuarios[u]["senha"] == p:
                st.session_state.logged_in = True
                st.session_state.user_name = u
                st.session_state.role = st.session_state.banco_usuarios[u]["role"]
                st.session_state.turno_trabalho = "1º TURNO" if st.session_state.banco_usuarios[u]["role"] == "admin" else st.session_state.banco_usuarios[u]["turno_fixo"]
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

def main():
    if st.session_state.logged_in:
        st.sidebar.title("Zion Operações")
        if st.sidebar.button("Lançamentos do Turno", use_container_width=True):
            st.session_state.menu_atual = "Lançamentos"
            st.rerun()
        if st.session_state.role == "admin" and st.sidebar.button("Global (Consolidado)", use_container_width=True):
            st.session_state.menu_atual = "Global"
            st.rerun()
        if st.sidebar.button("Sair", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
            
        if st.session_state.menu_atual == "Lançamentos": bloco_painel_poroes(st.session_state.turno_trabalho)
        else: bloco_consolidado_geral()
    else:
        bloco_login()

if __name__ == "__main__":
    main()
