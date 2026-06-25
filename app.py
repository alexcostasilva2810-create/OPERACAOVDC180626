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
# URL DO SEU GOOGLE APPS SCRIPT
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
            
            for c in COLUNAS_PADRAO:
                if c not in df.columns:
                    df[c] = ""
            
            return df[COLUNAS_PADRAO]
    except Exception:
        pass
    return pd.DataFrame(columns=COLUNAS_PADRAO)

def atualizar_planilha_nuvem(df_novo):
    try:
        df_envio = df_novo[COLUNAS_PADRAO].copy()
        
        for c in df_envio.columns:
            df_envio[c] = df_envio[c].fillna("")
            df_envio[c] = df_envio[c].astype(str).str.replace("None", "").str.replace("NaN", "")
            
        dados_json = df_envio.to_dict(orient="records")
        response = requests.post(URL_WEB_APP, json=dados_json, timeout=15)
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
    df_atual = st.session_state.dados_operacao.copy()

    st.sidebar.title("Zion Operações")
    st.sidebar.write(f"🟢 **Usuário:** {st.session_state.usuario_atual}")
    
    if st.sidebar.button("🔄 Atualizar Dados Nuvem", use_container_width=True):
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
    
    user_info = st.session_state.usuarios_db[st.session_state.usuario_atual]

    # --- TELA: LANÇAMENTOS DO TURNO ---
    if st.session_state.menu_atual == "Lançamentos do Turno" and st.session_state.cargo_atual != "visualizador_global":
        if user_info["turno"] != "Todos":
            turno_trabalho = user_info["turno"]
        else:
            turno_trabalho = st.sidebar.selectbox("Visualizar Turno", ["1º TURNO", "2º TURNO"])
            
        st.header(f"Lançamentos Atuais - {turno_trabalho}")
        
        with st.expander("▼ Novo Lançamento (5 Porões)", expanded=True):
            col_data, col_p1, col_p2, col_p3, col_p4, col_p5 = st.columns(6)
            
            fuso_local = datetime.utcnow() - timedelta(hours=3)
            
            with col_data:
                data_lanc = st.date_input("Data", value=fuso_local, format="DD/MM/YYYY")
            with col_p1:
                p1_input = st.number_input("Porão 1 (t)", min_value=0.0, step=50.0, value=None)
            with col_p2:
                p2_input = st.number_input("Porão 2 (t)", min_value=0.0, step=50.0, value=None)
            with col_p3:
                p3_input = st.number_input("Porão 3 (t)", min_value=0.0, step=50.0, value=None)
            with col_p4:
                p4_input = st.number_input("Porão 4 (t)", min_value=0.0, step=50.0, value=None)
            with col_p5:
                p5_input = st.number_input("Porão 5 (t)", min_value=0.0, step=50.0, value=None)
                
            btn_gravar = st.button("Gravar Lançamento", type="primary", use_container_width=True)
            
        if btn_gravar:
            p1 = p1_input if p1_input is not None else 0.0
            p2 = p2_input if p2_input is not None else 0.0
            p3 = p3_input if p3_input is not None else 0.0
            p4 = p4_input if p4_input is not None else 0.0
            p5 = p5_input if p5_input is not None else 0.0
            
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
                "Hora do Registro": fuso_local.strftime("%H:%M:%S")
            }
            
            novo_df_linha = pd.DataFrame([novo_registro])
            st.session_state.dados_operacao = pd.concat([st.session_state.dados_operacao, novo_df_linha], ignore_index=True)
            
            if atualizar_planilha_nuvem(st.session_state.dados_operacao):
                st.success("Lançamento efetuado e enviado com sucesso! 🚀")
            else:
                st.error("Erro ao sincronizar com o Google Sheets.")
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

    # --- TELA: GLOBAL CONSOLIDADO (CORRIGIDA) ---
    elif st.session_state.menu_atual == "Global (Consolidado)":
        st.header("Painel Gerencial Global (5 Porões)")
        
        # Correção matemática de segurança: garante conversão numérica estrita antes de realizar somas
        if not df_atual.empty:
            for p in ["Porão 1", "Porão 2", "Porão 3", "Porão 4", "Porão 5"]:
                df_atual[p] = pd.to_numeric(df_atual[p], errors='coerce').fillna(0.0)
            
            total_p1 = df_atual["Porão 1"].sum()
            total_p2 = df_atual["Porão 2"].sum()
            total_p3 = df_atual["Porão 3"].sum()
            total_p4 = df_atual["Porão 4"].sum()
            total_p5 = df_atual["Porão 5"].sum()
            
            # Recalcula o saldo de forma pura diretamente pela soma real dos porões homologados
            total_lancado = total_p1 + total_p2 + total_p3 + total_p4 + total_p5
        else:
            total_p1 = total_p2 = total_p3 = total_p4 = total_p5 = total_lancado = 0.0
            
        quanto_falta = max(0.0, REFERENCIA_CONTRATUAL - total_lancado)
        porcentagem_alcancada = (total_lancado / REFERENCIA_CONTRATUAL) * 100 if REFERENCIA_CONTRATUAL > 0 else 0.0

        col_m1, col_m2, col_m3, col_m4, col_m5, col_mt = st.columns(6)
        col_m1.metric("Total Porão 1", f"{total_p1:,.0f} t".replace(",", "."))
        col_m2.metric("Total Porão 2", f"{total_p2:,.0f} t".replace(",", "."))
        col_m3.metric("Total Porão 3", f"{total_p3:,.0f} t".replace(",", "."))
        col_m4.metric("Total Porão 4", f"{total_p4:,.0f} t".replace(",", "."))
        col_m5.metric("Total Porão 5", f"{total_p5:,.0f} t".replace(",", "."))
        col_mt.metric("TOTAL JÁ LANÇADO", f"{total_lancado:,.0f} t".replace(",", "."))
        
        col_ref, col_porc, col_falta = st.columns(3)
        with col_ref:
            st.info(f"**REFERÊNCIA CONTRATUAL:**\n### {REFERENCIA_CONTRATUAL:,.0f} t".replace(",", "."))
        with col_porc:
            st.info(f"**% ALCANÇADO DA META:**\n### {porcentagem_alcancada:.2f}%".replace(".", ","))
        with col_falta:
            st.warning(f"**QUANTO FALTA ATINGIR:**\n### {quanto_falta:,.0f} t".replace(",", "."))
            
        st.markdown("---")
        
        data_atual = (datetime.utcnow() - timedelta(hours=3)).strftime("%d/%m/%Y %H:%M:%S")
        html_relatorio = f"""
        <script>
        function imprimirRelatorio() {{
            var win = window.open("", "_blank");
            win.document.write("<html><head><title>Relatorio Global Zion</title>");
            win.document.write("<style>body{{font-family:Arial,sans-serif;padding:30px;}} table{{width:100%;border-collapse:collapse;margin-top:20px;}} th,td{{border:1px solid #ddd;padding:10px;text-align:left;}} th{{background-color:#006633;color:white;}}</style>");
            win.document.write("</head><body>");
            win.document.write("<h2>ZION TECNOLOGIA PORTUÁRIA</h2>");
            win.document.write("<p><b>Relatório Gerencial Emitido em:</b> {data_atual}</p>");
            win.document.write("<p><b>Emitido por:</b> {st.session_state.usuario_atual}</p>");
            win.document.write("<h3>Resumo de Production por Porão</h3>");
            win.document.write("<table><tr><th>Local de Carga</th><th>Volume Operado (t)</th></tr>");
            win.document.write("<tr><td>Porão 1</td><td>{total_p1:,.0f} t</td></tr>".replace(",", "."));
            win.document.write("<tr><td>Porão 2</td><td>{total_p2:,.0f} t</td></tr>".replace(",", "."));
            win.document.write("<tr><td>Porão 3</td><td>{total_p3:,.0f} t</td></tr>".replace(",", "."));
            win.document.write("<tr><td>Porão 4</td><td>{total_p4:,.0f} t</td></tr>".replace(",", "."));
            win.document.write("<tr><td>Porão 5</td><td>{total_p5:,.0f} t</td></tr>".replace(",", "."));
            win.document.write("</table>");
            win.document.write("<h3>Indicadores Contratuais</h3>");
            win.document.write("<table>");
            win.document.write("<tr><td><b>TOTAL JÁ LANÇADO</b></td><td><b>{total_lancado:,.0f} t</b></td></tr>".replace(",", "."));
            win.document.write("<tr><td>Referência Contratual</td><td>{REFERENCIA_CONTRATUAL:,.0f} t</td></tr>".replace(",", "."));
            win.document.write("<tr><td>Percentual Alcançado</td><td>{porcentagem_alcancada:.2f}%</td></tr>".replace(".", ","));
            win.document.write("<tr><td>Quanto Falta Atingir</td><td>{quanto_falta:,.0f} t</td></tr>".replace(",", "."));
            win.document.write("</table>");
            win.document.write("</body></html>");
            win.document.close();
            win.print();
        }}
        </script>
        <button onclick="imprimirRelatorio()" style="width:100%; background-color:#000; color:#00FF66; border:2px solid #00FF66; padding:10px; font-weight:bold; border-radius:5px; cursor:pointer;">
            📄 Imprimir / Salvar como PDF do Relatório
        </button>
        """
        st.components.v1.html(html_relatorio, height=60)
            
        st.markdown("---")
        st.subheader("Histórico de Lançamentos Realizados")
        
        if not df_atual.empty:
            # Reorganização Estrita de Colunas: Força o dataframe a alinhar os dados com os cabeçalhos corretos da planilha
            df_atual = df_atual[COLUNAS_PADRAO]
            
            if st.session_state.cargo_atual == "admin":
                st.markdown("💡 *Marque a caixinha na coluna **Excluir** do registro que deseja remover e clique no botão abaixo.*")
                
                df_com_checkbox = df_atual.copy()
                df_com_checkbox.insert(0, "Excluir", False)
                df_com_checkbox["_id_real_planilha"] = df_atual.index
                
                # data_editor configurado explicitamente para não bagunçar a ordem das colunas mapeadas
                df_editado_global = st.data_editor(
                    df_com_checkbox,
                    use_container_width=True,
                    hide_index=True,
                    disabled=[c for c in df_com_checkbox.columns if c != "Excluir"],
                    column_config={"_id_real_planilha": None}
                )
                
                if st.button("🗑️ Excluir Registros Marcados Permanentemente", type="primary"):
                    linhas_marcadas = df_editado_global[df_editado_global["Excluir"] == True]
                    
                    if not linhas_marcadas.empty:
                        indices_originais_remover = linhas_marcadas["_id_real_planilha"].tolist()
                        df_atualizado = st.session_state.dados_operacao.drop(index=indices_originais_remover).reset_index(drop=True)
                        
                        if atualizar_planilha_nuvem(df_atualizado):
                            st.session_state.dados_operacao = df_atualizado
                            st.success(f"Sucesso! {len(indices_originais_remover)} registro(s) deletado(s) da planilha!")
                            st.rerun()
                        else:
                            st.error("Erro ao sincronizar com o Google Sheets.")
                    else:
                        st.warning("Nenhum registro foi marcado no quadradinho para exclusão.")
            else:
                st.dataframe(df_atual, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum dado lançado nos turnos até o momento.")
