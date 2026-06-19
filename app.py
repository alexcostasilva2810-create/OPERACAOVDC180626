import streamlit as st
import pandas as pd
from io import BytesIO
import base64

# =====================================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================================
st.set_page_config(page_title="Zion Tecnologia - Gestão Portuária", page_icon="🚢", layout="wide")

# =====================================================================
# BLOCO: ESTILIZAÇÃO VISUAL (CSS DE ALTO CONTRASTE EM VERDE)
# =====================================================================
def aplicar_estilo_visual():
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        }
        p, label, .stText, p code, .stMarkdown p {
            color: #00ff66 !important;
            font-weight: bold !important;
            font-size: 16px !important;
        }
        .stTextInput input, .stNumberInput input, .stSelectbox div {
            color: #00ff66 !important;
            font-weight: bold !important;
            background-color: #1e293b !important;
        }
        [data-testid="stMetricValue"] {
            color: #00ff66 !important;
            font-weight: bold !important;
            font-size: 32px !important;
        }
        [data-testid="stMetricLabel"] p {
            color: #38bdf8 !important;
        }
        table {
            color: #00ff66 !important;
            font-weight: bold !important;
        }
        th {
            color: #38bdf8 !important;
            font-size: 16px !important;
        }
        td {
            color: #00ff66 !important;
            font-size: 15px !important;
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
# FUNÇÃO AUXILIAR: GERAÇÃO DE HTML PARA O PDF CONSOLIDADO
# =====================================================================
def gerar_html_relatorio(p1, p2, p3, p4, saldo, df_combinado):
    linhas_tabela = ""
    for _, row in df_combinado.iterrows():
        linhas_tabela += f"""
        <tr>
            <td>{row['Dia']}</td>
            <td>{row['Porão 1']}</td>
            <td>{row['Porão 2']}</td>
            <td>{row['Porão 3']}</td>
            <td>{row['Porão 4']}</td>
            <td><strong>{row['Saldo']}</strong></td>
        </tr>
        """
        
    html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{ size: A4; margin: 20mm 15mm; }}
            body {{ font-family: Arial, sans-serif; color: #1e293b; }}
            .header {{ border-bottom: 3px solid #0284c7; padding-bottom: 10px; margin-bottom: 25px; }}
            h1 {{ color: #0f172a; font-size: 22pt; margin: 0; text-transform: uppercase; }}
            .sub {{ color: #64748b; font-size: 11pt; margin-top: 5px; font-weight: bold; }}
            .resumo {{ width: 100%; border-collapse: collapse; margin-bottom: 30px; margin-top: 15px; }}
            .resumo td {{ background-color: #f8fafc; border: 1px solid #e2e8f0; padding: 12px; text-align: center; }}
            .resumo .val {{ font-size: 14pt; font-weight: bold; color: #0284c7; }}
            .resumo .total-val {{ font-size: 15pt; font-weight: bold; color: #16a34a; }}
            table.dados {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            table.dados th {{ background-color: #0f172a; color: white; padding: 10px; font-size: 10pt; text-align: left; }}
            table.dados td {{ padding: 10px; border: 1px solid #e2e8f0; font-size: 10pt; }}
            table.dados tr:nth-child(even) {{ background-color: #f8fafc; }}
            .footer {{ margin-top: 40px; text-align: center; font-size: 9pt; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Relatório Consolidado de carregamento</h1>
            <div class="sub">Zion Tecnologia — Sistema de Gestão Portuária Integrada</div>
        </div>
        
        <h3>Resumo de Volumes por Porão</h3>
        <table class="resumo">
            <tr>
                <td><strong>Porão 1</strong><br><span class="val">{p1} t</span></td>
                <td><strong>Porão 2</strong><br><span class="val">{p2} t</span></td>
                <td><strong>Porão 3</strong><br><span class="val">{p3} t</span></td>
                <td><strong>Porão 4</strong><br><span class="val">{p4} t</span></td>
                <td style="background-color: #f0fdf4; border: 1px solid #bbf7d0;">
                    <strong style="color: #166534;">Saldo Global</strong><br>
                    <span class="total-val">{saldo} t</span>
                </div>
            </tr>
        </table>

        <h3>Demonstrativo Geral de Lançamentos</h3>
        <table class="dados">
            <thead>
                <tr>
                    <th>Data</th>
                    <th>Porão 1 (t)</th>
                    <th>Porão 2 (t)</th>
                    <th>Porão 3 (t)</th>
                    <th>Porão 4 (t)</th>
                    <th>Saldo Diário (t)</th>
                </tr>
            </thead>
            <tbody>
                {linhas_tabela}
                <tr style="background-color: #e2e8f0; font-weight: bold;">
                    <td>TOTAL GERAL</td>
                    <td>{p1}</td>
                    <td>{p2}</td>
                    <td>{p3}</td>
                    <td>{p4}</td>
                    <td style="color: #16a34a;">{saldo}</td>
                </tr>
            </tbody>
        </table>
        
        <div class="footer">
            Relatório gerado eletronicamente pela plataforma Zion Tecnologia.
        </div>
    </body>
    </html>
    """
    return html

# =====================================================================
# MÓDULO 3: VISÃO CONSOLIDADA + EXPORTAÇÃO EM PDF
# =====================================================================
def bloco_consolidado_geral():
    st.markdown("## 🌍 Painel Gerencial Consolidado (Turno 1 + Turno 2)")
    
    df1 = st.session_state.tabela_turno_1.copy()
    df2 = st.session_state.tabela_turno_2.copy()
    
    # Agrupando e unificando as tabelas de ambos os turnos para exibição unificada
    df_combinado = pd.concat([df1, df2], ignore_index=True)
    if not df_combinado.empty:
        df_combinado[["Porão 1", "Porão 2", "Porão 3", "Porão 4", "Saldo"]] = df_combinado[["Porão 1", "Porão 2", "Porão 3", "Porão 4", "Saldo"]].apply(pd.to_numeric)
        df_combinado = df_combinado.groupby("Dia", as_index=False).sum()
    
    p1_total = pd.to_numeric(df1["Porão 1"]).sum() + pd.to_numeric(df2["Porão 1"]).sum()
    p2_total = pd.to_numeric(df1["Porão 2"]).sum() + pd.to_numeric(df2["Porão 2"]).sum()
    p3_total = pd.to_numeric(df1["Porão 3"]).sum() + pd.to_numeric(df2["Porão 3"]).sum()
    p4_total = pd.to_numeric(df1["Porão 4"]).sum() + pd.to_numeric(df2["Porão 4"]).sum()
    saldo_geral = p1_total + p2_total + p3_total + p4_total

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Porão 1", f"{p1_total} t")
    c2.metric("Total Porão 2", f"{p2_total} t")
    c3.metric("Total Porão 3", f"{p3_total} t")
    c4.metric("Total Porão 4", f"{p4_total} t")
    c5.metric("SALDO GLOBAL NAVIO", f"{saldo_geral} t")

    st.markdown("---")
    
    st.markdown("#### Histórico Combinado por Dia")
    if not df_combinado.empty:
        st.table(df_combinado)
        
        # Gerar o código HTML do relatório estruturado
        html_doc = gerar_html_relatorio(p1_total, p2_total, p3_total, p4_total, saldo_geral, df_combinado)
        
        try:
            from weasyprint import HTML
            pdf_buffer = BytesIO()
            HTML(string=html_doc).write_pdf(pdf_buffer)
            
            st.download_button(
                label="📥 Exportar Relatório em PDF",
                data=pdf_buffer.getvalue(),
                file_name="Relatorio_Consolidado_Carregamento.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception:
            # Fallback caso os binários do WeasyPrint não estejam instalados localmente na máquina durante o teste
            st.warning("⚠️ Instale as dependências do WeasyPrint para habilitar a renderização nativa de PDF.")
    else:
        st.info("Aguardando lançamentos dos turnos para consolidar os relatórios.")

# =====================================================================
# MÓDULO 2: LANÇAMENTOS POR PORÃO
# =====================================================================
def bloco_painel_poroes(turno_atual):
    st.markdown(f"### 📊 Lançamentos Atuais - {turno_atual}")
    chave_tabela = 'tabela_turno_1' if turno_atual == "1º TURNO" else 'tabela_turno_2'
    df_atual = st.session_state[chave_tabela]

    with st.expander("➕ Inserir Novo Lançamento de Toneladas", expanded=True):
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1: data_lan = st.date_input("Data da Operação", format="DD/MM/YYYY", key=f"dt_{turno_atual}")
        with col2: v1 = st.number_input("Toneladas Porão 1", min_value=0, step=50, key=f"p1_{turno_atual}")
        with col3: v2 = st.number_input("Toneladas Porão 2", min_value=0, step=50, key=f"p2_{turno_atual}")
        with col4: v3 = st.number_input("Toneladas Porão 3", min_value=0, step=50, key=f"p3_{turno_atual}")
        with col5: v4 = st.number_input("Toneladas Porão 4", min_value=0, step=50, key=f"p4_{turno_atual}")
        
        if st.button("Gravar Lançamento", use_container_width=True, key=f"btn_{turno_atual}"):
            nova = pd.DataFrame([{"Dia": data_lan.strftime("%d/%m/%Y"), "Porão 1": v1, "Porão 2": v2, "Porão 3": v3, "Porão 4": v4, "Saldo": v1+v2+v3+v4}])
            st.session_state[chave_tabela] = pd.concat([df_atual, nova], ignore_index=True)
            st.success("Dados gravados com sucesso!")
            st.rerun()

    if not df_atual.empty:
        df_vis = df_atual.copy()
        colunas_num = ["Porão 1", "Porão 2", "Porão 3", "Porão 4", "Saldo"]
        df_vis[colunas_num] = df_vis[colunas_num].apply(pd.to_numeric)
        
        soma_row = {"Dia": "TOTAL DO TURNO", "Porão 1": df_vis["Porão 1"].sum(), "Porão 2": df_vis["Porão 2"].sum(), 
                    "Porão 3": df_vis["Porão 3"].sum(), "Porão 4": df_vis["Porão 4"].sum(), "Saldo": df_vis["Saldo"].sum()}
        df_vis = pd.concat([df_vis, pd.DataFrame([soma_row])], ignore_index=True)
        st.table(df_vis)
    else:
        st.info("Nenhum registro lançado para este turno hoje.")

# =====================================================================
# MÓDULO 1: CONTROLE DE ACESSO
# =====================================================================
def bloco_login():
    st.markdown('<div class="custom-box">', unsafe_allow_html=True)
    st.title("Zion Tecnologia")
    u = st.text_input("Nome de Usuário")
    p = st.text_input("Senha do Sistema", type="password")
    t = st.selectbox("Selecione seu Turno de Trabalho", ["1º TURNO", "2º TURNO"])
    if st.button("Entrar no Sistema", use_container_width=True):
        banco = st.session_state.banco_usuarios
        if u in banco and banco[u]["senha"] == p and banco[u]["turno"] == t:
            st.session_state.logged_in, st.session_state.user_name, st.session_state.turno = True, u, t
            st.rerun()
        else: st.error("Dados incorretos ou turno divergente.")
    st.markdown('</div>', unsafe_allow_html=True)

def bloco_cadastro():
    st.markdown('<div class="custom-box">', unsafe_allow_html=True)
    st.subheader("Cadastrar Novo Operador")
    nu = st.text_input("Definir Usuário")
    np = st.text_input("Definir Senha", type="password")
    nt = st.selectbox("Vincular a qual Turno?", ["1º TURNO", "2º TURNO"])
    if st.button("Salvar Operador", use_container_width=True):
        st.session_state.banco_usuarios[nu] = {"senha": np, "turno": nt}
        st.success("Novo operador registrado!")
    st.markdown('</div>', unsafe_allow_html=True)

# =====================================================================
# ORQUESTRADOR CENTRAL
# =====================================================================
def main():
    aplicar_estilo_visual()
    inicializar_dados()

    if st.session_state.logged_in:
        st.sidebar.title("Zion Operações")
        st.sidebar.markdown(f"**Operador:** {st.session_state.user_name}")
        st.sidebar.markdown(f"**Turno:** {st.session_state.turno}")
        if st.sidebar.button("Efetuar Logout (Sair)", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
        
        aba1, aba2 = st.tabs(["📋 Realizar Lançamentos (Meu Turno)", "📊 Visão Master (Consolidado Global)"])
        with aba1: bloco_painel_poroes(st.session_state.turno)
        with aba2: bloco_consolidado_geral()
    else:
        aba_l, aba_c = st.tabs(["Login de Acesso", "Cadastro de Operadores"])
        with aba_l: bloco_login()
        with aba_c: bloco_cadastro()

if __name__ == "__main__":
    main()
