import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from streamlit_gsheets import GSheetsConnection

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
# CONTROLE DE ESTADO DA SESSÃO E BANCO DE USUÁRIOS
# -----------------------------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "usuario_atual" not in st.session_state:
    st.session_state.usuario_atual = ""

if "cargo_atual" not in st.session_state:
    st.session_state.cargo_atual = ""

if "menu_atual" not in st.session_state:
    st.session_state.menu_atual = "Lançamentos do Turno"

if "usuarios_db" not in st.session_state:
    st.session_state.usuarios_db = {
        "admin": {"senha": "10000", "cargo": "admin", "turno": "Todos"},
        "Alex": {"senha": "1234", "cargo": "admin", "turno": "Todos"},
        "operador1": {"senha": "111", "cargo": "operador", "turno": "1º TURNO"},
        "operador2": {"senha": "222", "cargo": "operador", "turno": "2º TURNO"},
        "chico": {"senha": "3322", "cargo": "operador", "turno": "1º TURNO"},
    }

REFERENCIA_CONTRATUAL = 50000.0

# -----------------------------------------------------------------------------
# CONEXÃO COM O GOOGLE SHEETS
# -----------------------------------------------------------------------------
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception:
    conn = None

def carregar_dados_nuvem():
    if conn:
        try:
            df = conn.read(ttl=0)
            if df.empty:
                return pd.DataFrame(columns=["Turno", "Dia", "Porão 1", "Porão 2", "Porão 3", "Porão 4", "Porão 5", "Saldo", "Usuário", "Hora do Registro"])
            
            colunas_numéricas = ["Porão 1", "Porão 2", "Porão 3", "Porão 4", "Porão 5", "Saldo"]
            for col in colunas_numéricas:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
            return df
        except Exception:
            pass
    return pd.DataFrame(columns=["Turno", "Dia", "Porão 1", "Porão 2", "Porão 3", "Porão 4", "Porão 5", "Saldo", "Usuário", "Hora do Registro"])

def atualizar_planilha_nuvem(df_novo):
    if conn:
        try:
            conn.update(data=df_novo)
            return True
        except Exception:
            return False
    return False

# Inicializa os dados na sessão
if "dados_operacao" not in st.session_state:
    st.session_state.dados_operacao = carregar_dados_nuvem()

# -----------------------------------------------------------------------------
# TELA DE LOGIN (VÍDEO 2)
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
            if user_input in db and db[user_input]["senha"] == pass_input:
                st.session_state.logged_in = True
                st.session_state.usuario_atual = user_input
                st.session_state.cargo_atual = db[user_input]["cargo"]
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")

# -----------------------------------------------------------------------------
# INTERFACE DO SISTEMA LOGADO
# -----------------------------------------------------------------------------
else:
    df_atual = st.session_state.dados_operacao

    st.sidebar.title("Zion Operações")
    st.sidebar.write(f"🟢 **Usuário:** {st.session_state.usuario_atual} ({st.session_state.cargo_atual.upper()})")
    
    if st.sidebar.button("Lançamentos do Turno", use_container_width=True):
        st.session_state.menu_atual = "Lançamentos do Turno"
        
    if st.session_state.cargo_atual == "admin":
        if st.sidebar.button("Global (Consolidado)", use_container_width=True):
            st.session_state.menu_atual = "Global (Consolidado)"
        if st.sidebar.button("Cadastrar Operador", use_container_width=True):
            st.session_state.menu_atual = "Cadastrar Operador"
        
    if st.sidebar.button("Sair", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.usuario_atual = ""
        st.session_state.cargo_atual = ""
        st.rerun()

    st.sidebar.markdown("---")
    
    user_info = st.session_state.usuarios_db[st.session_state.usuario_atual]
    if user_info["turno"] != "Todos":
        turno_trabalho = user_info["turno"]
    else:
        turno_trabalho = st.sidebar.selectbox("Visualizar Turno", ["1º TURNO", "2º TURNO"])

    # -------------------------------------------------------------------------
    # MÓDULO LANÇAMENTOS DO TURNO
    # -------------------------------------------------------------------------
    if st.session_state.menu_atual == "Lançamentos do Turno":
        st.header(f"Lançamentos Atuais - {turno_trabalho}")
        
        with st.expander("▼ Novo Lançamento (5 Porões)", expanded=True):
            col_data, col_p1, col_p2, col_p3, col_p4, col_p5 = st.columns(6)
            
            with col_data:
                data_lanc = st.date_input("Data", value=datetime.now(), format="DD/MM/YYYY")
            with col_p1:
                p1 = st.number_input("Porão 1 (t)", min_value=0.0, step=50.0, value=0.0)
            with col_p2:
                p2 = st.number_input("Porão 2 (t)", min_value=0.0, step=50.0, value=0.0)
            with col_p3:
                p3 = st.number_input("Porão 3 (t)", min_value=0.0, step=50.0, value=0.0)
            with col_p4:
                p4 = st.number_input("Porão 4 (t)", min_value=0.0, step=50.0, value=0.0)
            with col_p5:
                p5 = st.number_input("Porão 5 (t)", min_value=0.0, step=50.0, value=0.0)
                
            btn_gravar = st.button("Gravar Lançamento", type="primary", use_container_width=True)
            
        if btn_gravar:
            saldo_lancamento = p1 + p2 + p3 + p4 + p5
            
            novo_registro = {
                "Turno": turno_trabalho,
                "Dia": data_lanc.strftime("%d/%m/%Y"),
                "Porão 1": p1,
                "Porão 2": p2,
                "Porão 3": p3,
                "Porão 4": p4,
                "Porão 5": p5,
                "Saldo": saldo_lancamento,
                "Usuário": st.session_state.usuario_atual,
                "Hora do Registro": datetime.now().strftime("%H:%M:%S")
            }
            
            novo_df_linha = pd.DataFrame([novo_registro])
            st.session_state.dados_operacao = pd.concat([st.session_state.dados_operacao, novo_df_linha], ignore_index=True)
            
            atualizar_planilha_nuvem(st.session_state.dados_operacao)
            
            st.success("Lançamento efetuado com sucesso! 🚀")
            st.rerun()

        st.subheader("Histórico do Turno")
        if not df_atual.empty and "Turno" in df_atual.columns:
            df_turno = df_atual[df_atual["Turno"] == turno_trabalho]
            if not df_turno.empty:
                st.dataframe(df_turno, use_container_width=True, hide_index=True)
            else:
                st.info(f"Nenhum registro lançado ainda para o {turno_trabalho}.")
        else:
            st.info(f"Nenhum registro lançado ainda para o {turno_trabalho}.")

        st.markdown("---")
        if not df_atual.empty and "Turno" in df_atual.columns:
            df_turno_edit = df_atual[df_atual["Turno"] == turno_trabalho]
            if not df_turno_edit.empty:
                opcoes_edicao = [f"Linha {idx} - Data: {row['Dia']} (Saldo: {row['Saldo']})" for idx, row in df_turno_edit.iterrows()]
                selecionado = st.selectbox("Selecione um lançamento para editar:", opcoes_edicao)
                if selecionado:
                    st.button("Editar Linha", use_container_width=True)

    # -------------------------------------------------------------------------
    # MÓDULO GLOBAL (Apenas Admins acessam)
    # -------------------------------------------------------------------------
    elif st.session_state.menu_atual == "Global (Consolidado)" and st.session_state.cargo_atual == "admin":
        st.header("Painel Gerencial Global (5 Porões)")
        
        if not df_atual.empty:
            total_p1 = df_atual["Porão 1"].sum() if "Porão 1" in df_atual.columns else 0.0
            total_p2 = df_atual["Porão 2"].sum() if "Porão 2" in df_atual.columns else 0.0
            total_p3 = df_atual["Porão 3"].sum() if "Porão 3" in df_atual.columns else 0.0
            total_p4 = df_atual["Porão 4"].sum() if "Porão 4" in df_atual.columns else 0.0
            total_p5 = df_atual["Porão 5"].sum() if "Porão 5" in df_atual.columns else 0.0
            total_lancado = df_atual["Saldo"].sum() if "Saldo" in df_atual.columns else 0.0
        else:
            total_p1 = total_p2 = total_p3 = total_p4 = total_p5 = total_lancado = 0.0
            
        quanto_falta = max(0.0, REFERENCIA_CONTRATUAL - total_lancado)

        col_m1, col_m2, col_m3, col_m4, col_m5, col_mt = st.columns(6)
        col_m1.metric("Total Porão 1", f"{total_p1:,.0f} t".replace(",", "."))
        col_m2.metric("Total Porão 2", f"{total_p2:,.0f} t".replace(",", "."))
        col_m3.metric("Total Porão 3", f"{total_p3:,.0f} t".replace(",", "."))
        col_m4.metric("Total Porão 4", f"{total_p4:,.0f} t".replace(",", "."))
        col_m5.metric("Total Porão 5", f"{total_p5:,.0f} t".replace(",", "."))
        col_mt.metric("TOTAL JÁ LANÇADO", f"{total_lancado:,.0f} t".replace(",", "."))
        
        col_ref, col_falta = st.columns(2)
        with col_ref:
            st.info(f"**REFERÊNCIA CONTRATUAL:**\n### {REFERENCIA_CONTRATUAL:,.0f} t".replace(",", "."))
        with col_falta:
            st.warning(f"**QUANTO FALTA ATINGIR:**\n### {quanto_falta:,.0f} t".replace(",", "."))
            
        st.markdown("---")
        st.subheader("Histórico de Lançamentos Realizados")
        
        if not df_atual.empty:
            st.dataframe(df_atual, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum dado lançado nos turnos até o momento.")
            
        st.button("Exportar Relatório Global em PDF", type="secondary", use_container_width=True)

    # -------------------------------------------------------------------------
    # MÓDULO CADASTRO DE OPERADORES (Apenas Admins acessam)
    # -------------------------------------------------------------------------
    elif st.session_state.menu_atual == "Cadastrar Operador" and st.session_state.cargo_atual == "admin":
        st.header("Cadastrar Novo Operador")
        
        novo_user = st.text_input("Definir Usuário", key="cad_user")
        nova_senha = st.text_input("Definir Senha", type="password", key="cad_pass")
        cargo_selecionado = st.selectbox("Cargo", ["operador", "admin"], key="cad_cargo")
        
        if cargo_selecionado == "admin":
            turno_fixo = "Todos"
            st.write("📌 *Administradores possuem acesso global a ambos os turnos.*")
        else:
            turno_fixo = st.selectbox("Turno Fixo", ["1º TURNO", "2º TURNO"], key="cad_turno")
        
        if st.button("Salvar Operador", use_container_width=True):
            if novo_user and nova_senha:
                st.session_state.usuarios_db[novo_user] = {
                    "senha": nova_senha,
                    "cargo": cargo_selecionado,
                    "turno": turno_fixo
                }
                st.success(f"Usuário '{novo_user}' cadastrado com sucesso! Ele já pode fazer login.")
            else:
                st.error("Preencha todos os campos para cadastrar.")
