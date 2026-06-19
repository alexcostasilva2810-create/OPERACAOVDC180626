import streamlit as st
import pandas as pd
from io import BytesIO

# =====================================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================================
st.set_page_config(page_title="Zion Tecnologia - Gestão Portuária", page_icon="🚢", layout="wide")

# =====================================================================
# BLOCO: ESTILIZAÇÃO VISUAL (CSS)
# =====================================================================
def aplicar_estilo_visual():
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #ffffff;
        }
        .metric-card {
            background-color: rgba(30, 41, 59, 0.8);
            border: 1px solid #38bdf8;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .custom-box {
            background-color: rgba(30, 41, 59, 0.6);
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        h1, h2, h3 { color: #38bdf8 !important; }
        </style>
        """,
        unsafe_allow_html=True
    )

# =====================================================================
# BLOCO: INICIALIZAÇÃO DO BANCO DE DADOS EM MEMÓRIA
# =====================================================================
def inicializar_dados():
    if 'banco_usuarios' not in st.session_state:
        st.session_state.banco_usuarios = {
            "admin": {"senha": "1234", "turno": "1º TURNO"},
            "alex": {"senha": "zion2026", "turno": "2º TURNO"}
        }
    
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'user_name' not in st.session_state: st.session_state.user_name = ""
    if 'turno' not in st.session_state: st.session_state.turno = ""

    colunas = ["Dia", "Porão 1", "Porão 2", "Porão 3", "Porão 4", "Saldo"]
    if 'tabela_turno_1' not in st.session_state:
        st.session_state.tabela_turno_1 = pd.DataFrame(columns=colunas)
    if 'tabela_turno_2' not in st.session_state:
        st.session_state.tabela_turno_2 = pd.DataFrame(columns=colunas)

# =====================================================================
# MÓDULO 3: VISÃO CONSOLIDADA (SOMA DOS DOIS TURNOS)
# =====================================================================
def bloco_consolidado_geral():
    st.markdown("## 🌍 Painel Gerencial Consolidado (Turno 1 + Turno 2)")
    
    df1 = st.session_state.tabela_turno_1
    df2 = st.session_state.tabela_turno_2
    
    # Cálculo das somas totais por porão
    p1_total = df1["Porão 1"].sum() + df2["Porão 1"].sum()
    p2_total = df1["Porão 2"].sum() + df2["Porão 2"].sum()
    p3_total = df1["Porão 3"].sum() + df2["Porão 3"].sum()
    p4_total = df1["Porão 4"].sum() + df2["Porão 4"].sum()
    saldo_geral = p1_total + p2_total + p3_total + p4_total

    # Exibição em Cartões Métricos
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Porão 1", f"{p1_total} t")
    c2.metric("Total Porão 2", f"{p2_total} t")
    c3.metric("Total Porão 3", f"{p3_total} t")
    c4.metric("Total Porão 4", f"{p4_total} t")
    c5.metric("SALDO GLOBAL", f"{saldo_geral} t", delta_color="normal")

    st.markdown("---")
    st.info("💡 Estes valores somam automaticamente as toneladas lançadas por todos os turnos cadastrados.")

# =====================================================================
# MÓDULO 2: LANÇAMENTOS (CORRIGIDO)
# =====================================================================
def bloco_painel_poroes(turno_atual):
    st.markdown(f"### 📊 Lançamentos Atuais - {turno_atual}")
    chave_tabela = 'tabela_turno_1' if turno_atual == "1º TURNO" else 'tabela_turno_2'
    df_atual = st.session_state[chave_tabela]

    with st.expander("➕ Novo Lançamento", expanded=False):
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1: data_lan = st.date_input("Data", format="DD/MM/YYYY", key=f"dt_{turno_atual}")
        with col2: v1 = st.number_input("P1", min_value=0, step=50, key=f"p1_{turno_atual}")
        with col3: v2 = st.number_input("P2", min_value=0, step=50, key=f"p2_{turno_atual}")
        with col4: v3 = st.number_input("P3", min_value=0, step=50, key=f"p3_{turno_atual}")
        with col5: v4 = st.number_input("P4", min_value=0, step=50, key=f"p4_{turno_atual}")
        
        if st.button("Gravar", use_container_width=True, key=f"btn_{turno_atual}"):
            nova = pd.DataFrame([{"Dia": data_lan.strftime("%d/%m/%Y"), "Porão 1": v1, "Porão 2": v2, "Porão 3": v3, "Porão 4": v4, "Saldo": v1+v2+v3+v4}])
            st.session_state[chave_tabela] = pd.concat([df_atual, nova], ignore_index=True)
            st.rerun()

    if not df_atual.empty:
        # Exibição com soma total do turno
        df_vis = df_atual.copy()
        soma_row = {"Dia": "TOTAL TURNO", "Porão 1": df_vis["Porão 1"].sum(), "Porão 2": df_vis["Porão 2"].sum(), 
                    "Porão 3": df_vis["Porão 3"].sum(), "Porão 4": df_vis["Porão 4"].sum(), "Saldo": df_vis["Saldo"].sum()}
        df_vis = pd.concat([df_vis, pd.DataFrame([soma_row])], ignore_index=True)
        st.table(df_vis)
    else:
        st.write("Sem dados para este turno.")

# =====================================================================
# BLOCOS DE LOGIN E CADASTRO (MÓDULO 1)
# =====================================================================
def bloco_login():
    st.markdown('<div class="custom-box">', unsafe_allow_html=True)
    st.title("Zion Tecnologia")
    u = st.text_input("Usuário")
    p = st.text_input("Senha", type="password")
    t = st.selectbox("Turno", ["1º TURNO", "2º TURNO"])
    if st.button("Entrar", use_container_width=True):
        banco = st.session_state.banco_usuarios
        if u in banco and banco[u]["senha"] == p and banco[u]["turno"] == t:
            st.session_state.logged_in, st.session_state.user_name, st.session_state.turno = True, u, t
            st.rerun()
        else: st.error("Erro nos dados ou Turno incorreto.")
    st.markdown('</div>', unsafe_allow_html=True)

def bloco_cadastro():
    st.markdown('<div class="custom-box">', unsafe_allow_html=True)
    st.subheader("Criar Usuário")
    nu = st.text_input("Novo Usuário")
    np = st.text_input("Nova Senha", type="password")
    nt = st.selectbox("Vincular Turno", ["1º TURNO", "2º TURNO"])
    if st.button("Cadastrar"):
        st.session_state.banco_usuarios[nu] = {"senha": np, "turno": nt}
        st.success("Cadastrado!")
    st.markdown('</div>', unsafe_allow_html=True)

# =====================================================================
# ORQUESTRADOR PRINCIPAL
# =====================================================================
def main():
    aplicar_estilo_visual()
    inicializar_dados()

    if st.session_state.logged_in:
        st.sidebar.title(f"Olá, {st.session_state.user_name}")
        st.sidebar.info(f"Logado no {st.session_state.turno}")
        if st.sidebar.button("Sair"):
            st.session_state.logged_in = False
            st.rerun()
        
        # Interface por Abas para os Módulos 2 e 3
        aba1, aba2 = st.tabs(["📋 Meu Turno (Lançamentos)", "📊 Consolidado Geral (Zion Master)"])
        
        with aba1:
            bloco_painel_poroes(st.session_state.turno)
            
        with aba2:
            bloco_consolidado_geral()
    else:
        aba_l, aba_c = st.tabs(["Login", "Cadastro"])
        with aba_l: bloco_login()
        with aba_c: bloco_cadastro()

if __name__ == "__main__":
    main()
