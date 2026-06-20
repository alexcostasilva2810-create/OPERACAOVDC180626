import streamlit as st
import pandas as pd
from datetime import datetime
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
        
        /* Centralizar Título específico da tela Global */
        .titulo-centralizado {
            text-align: center;
            color: #38bdf8 !important;
            font-weight: bold !important;
            margin-bottom: 25px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# =====================================================================
# BLOCO: BANCO DE DADOS EM MEMÓRIA (Atualizado com novas colunas)
# =====================================================================
def inicializar_dados():
    if 'banco_usuarios' not in st.session_state:
        st.session_state.banco_usuarios = {
            "admin": {"senha": "1234", "role": "admin"},
            "admin2": {"senha": "5678", "role": "admin"},
            "alex": {"senha": "zion2026", "turno_fixo": "1º TURNO", "role": "operador"},
            "Rubens Ferreira": {"senha": "8036", "turno_fixo": "2º TURNO", "role": "operador"}
        }
    
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'user_name' not in st.session_state: st.session_state.user_name = ""
    if 'turno_trabalho' not in st.session_state: st.session_state.turno_trabalho = "1º TURNO"
    if 'role' not in st.session_state: st.session_state.role = "operador"
    if 'menu_atual' not in st.session_state: st.session_state.menu_atual = "Lançamentos"

    colunas = ["Dia", "Porão 1", "Porão 2", "Porão 3", "Porão 4", "Saldo", "Usuario", "Hora"]
    if 'tabela_turno_1' not in st.session_state:
        st.session_state.tabela_turno_1 = pd.DataFrame(columns=colunas)
    if 'tabela_turno_2' not in st.session_state:
        st.session_state.tabela_turno_2 = pd.DataFrame(columns=colunas)
        
    if 'edit_mode' not in st.session_state: st.session_state.edit_mode = False
    if 'edit_index' not in st.session_state: st.session_state.edit_index = None

# =====================================================================
# REPORTLAB: GERADOR DO RELATÓRIO PDF CONSOLIDADO
# =====================================================================
def gerar_pdf_reportlab(p1, p2, p3, p4, saldo, df_combinado):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=40, bottomMargin=40)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#0f172a'), alignment=1, spaceAfter=20)
    heading_style = ParagraphStyle('HeadingStyle', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#0284c7'), spaceBefore=15, spaceAfter=10)
    normal_style = ParagraphStyle('NormalStyle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#1e293b'))

    story.append(Paragraph("Relatório Consolidado de Carregamento - Global", title_style))
    story.append(Paragraph("<b>Zion Tecnologia</b> — Sistema de Controle Portuário Integrado", normal_style))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("Resumo Acumulado por Porão", heading_style))
    dados_resumo = [['Porão 1', 'Porão 2', 'Porão 3', 'Porão 4', 'SALDO GLOBAL'], [f"{p1} t", f"{p2} t", f"{p3} t", f"{p4} t", f"{saldo} t"]]
    t_resumo = Table(dados_resumo, colWidths=[100, 100, 100, 100, 120])
    t_resumo.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_resumo)
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Demonstrativo Detalhado de Movimentações (Todos os Turnos)", heading_style))
    dados_tabela = [['Turno', 'Data', 'Porão 1', 'Porão 2', 'Porão 3', 'Porão 4', 'Saldo', 'Usuário', 'Hora']]
    
    for _, row in df_combinado.iterrows():
        usr = str(row.get('Usuario', '-'))
        hra = str(row.get('Hora', '-'))
        dados_tabela.append([
            str(row['Turno']), str(row['Dia']), 
            f"{int(row['Porão 1'])} t", f"{int(row['Porão 2'])} t", 
            f"{int(row['Porão 3'])} t", f"{int(row['Porão 4'])} t", 
            f"{int(row['Saldo'])} t", usr, hra
        ])
    
    t_dados = Table(dados_tabela, colWidths=[65, 65, 55, 55, 55, 55, 60, 75, 55])
    t_dados.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e293b')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    story.append(t_dados)
    doc.build(story)
    return buffer.getvalue()

# =====================================================================
# MÓDULO 3: VISÃO GLOBAL CONSOLIDADA (APENAS ADMINISTRADORES)
# =====================================================================
def bloco_consolidado_geral():
    # Cabeçalho centralizado e sem o ícone do globo terrestre
    st.markdown("<h2 class='titulo-centralizado'>Painel Gerencial Global (Turno 1 + Turno 2)</h2>", unsafe_allow_html=True)
    
    df1 = st.session_state.tabela_turno_1.copy()
    df1["Turno"] = "1º TURNO"
    
    df2 = st.session_state.tabela_turno_2.copy()
    df2["Turno"] = "2º TURNO"
    
    df_combinado = pd.concat([df1, df2], ignore_index=True)
    
    p1_total = pd.to_numeric(df1["Porão 1"]).sum() if not df1.empty else 0
    p1_total += pd.to_numeric(df2["Porão 1"]).sum() if not df2.empty else 0
    
    p2_total = pd.to_numeric(df1["Porão 2"]).sum() if not df1.empty else 0
    p2_total += pd.to_numeric(df2["Porão 2"]).sum() if not df2.empty else 0
    
    p3_total = pd.to_numeric(df1["Porão 3"]).sum() if not df1.empty else 0
    p3_total += pd.to_numeric(df2["Porão 3"]).sum() if not df2.empty else 0
    
    p4_total = pd.to_numeric(df1["Porão 4"]).sum() if not df1.empty else 0
    p4_total += pd.to_numeric(df2["Porão 4"]).sum() if not df2.empty else 0
    
    saldo_geral = p1_total + p2_total + p3_total + p4_total
    
    meta_referencia = 50000
    falta_atingir = meta_referencia - saldo_geral if (meta_referencia - saldo_geral) > 0 else 0

    # Grid de Indicadores Superiores
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Porão 1", f"{int(p1_total)} t")
    c2.metric("Total Porão 2", f"{int(p2_total)} t")
    c3.metric("Total Porão 3", f"{int(p3_total)} t")
    c4.metric("Total Porão 4", f"{int(p4_total)} t")
    c5.metric("TOTAL JÁ LANÇADO", f"{int(saldo_geral)} t")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Bloco de Referência (Abatimento)
    meta_col1, meta_col2 = st.columns(2)
    with meta_col1:
        st.metric("REFERÊNCIA CONTRATUAL", f"{meta_referencia} t")
    with meta_col2:
        st.metric("QUANTO FALTA ATINGIR", f"{int(falta_atingir)} t")

    st.markdown("---")
    st.markdown("#### Histórico de Todos os Lançamentos Realizados")
    
    if not df_combinado.empty:
        df_combinado[["Porão 1", "Porão 2", "Porão 3", "Porão 4", "Saldo"]] = df_combinado[["Porão 1", "Porão 2", "Porão 3", "Porão 4", "Saldo"]].apply(pd.to_numeric).fillna(0)
        
        # Tabela Detalhada atualizada com colunas extras para Usuário e Hora de Gravação
        html_table = """
        <table>
            <thead>
                <tr>
                    <th>Turno</th>
                    <th>Dia</th>
                    <th>Porão 1</th>
                    <th>Porão 2</th>
                    <th>Porão 3</th>
                    <th>Porão 4</th>
                    <th>Saldo</th>
                    <th>Usuário</th>
                    <th>Hora do Registro</th>
                </tr>
            </thead>
            <tbody>
        """
        for _, r in df_combinado.iterrows():
            usr = r.get('Usuario', '-') if pd.notna(r.get('Usuario')) else '-'
            hra = r.get('Hora', '-') if pd.notna(r.get('Hora')) else '-'
            
            html_table += f"""
                <tr>
                    <td>{r['Turno']}</td>
                    <td>{r['Dia']}</td>
                    <td>{int(r['Porão 1'])} t</td>
                    <td>{int(r['Porão 2'])} t</td>
                    <td>{int(r['Porão 3'])} t</td>
                    <td>{int(r['Porão 4'])} t</td>
                    <td>{int(r['Saldo'])} t</td>
                    <td>{usr}</td>
                    <td>{hra}</td>
                </tr>
            """
        html_table += "</tbody></table>"
        st.markdown(html_table, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        pdf_data = gerar_pdf_reportlab(p1_total, p2_total, p3_total, p4_total, saldo_geral, df_combinado)
        
        st.download_button(
            label="📥 Exportar Relatório Global em PDF",
            data=pdf_data,
            file_name="Relatorio_Global_Carregamento.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.info("Nenhum dado lançado nos turnos até o momento.")

# =====================================================================
# MÓDULO 2: OPERAÇÃO DE LANÇAMENTOS POR TURNO
# =====================================================================
def bloco_painel_poroes(turno_atual):
    st.markdown(f"<h2>📊 Lançamentos Atuais - {turno_atual}</h2>", unsafe_allow_html=True)
    chave_tabela = 'tabela_turno_1' if turno_atual == "1º TURNO" else 'tabela_turno_2'
    df_atual = st.session_state[chave_tabela]

    if st.session_state.edit_mode and st.session_state.edit_index is not None and st.session_state.edit_index < len(df_atual):
        row_edit = df_atual.iloc[st.session_state.edit_index]
        titulo_box = "✏️ Alterar Dados do Lançamento"
        texto_botao = "💾 Salvar Alterações"
        val_p1, val_p2, val_p3, val_p4 = int(row_edit["Porão 1"]), int(row_edit["Porão 2"]), int(row_edit["Porão 3"]), int(row_edit["Porão 4"])
    else:
        st.session_state.edit_mode = False
        st.session_state.edit_index = None
        titulo_box = "➕ Inserir Novo Lançamento de Toneladas"
        texto_botao = "Gravar Lançamento"
        val_p1, val_p2, val_p3, val_p4 = 0, 0, 0, 0

    with st.expander(titulo_box, expanded=True):
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1: data_lan = st.date_input("Data da Operação", format="DD/MM/YYYY", key=f"dt_{turno_atual}")
        with col2: v1 = st.number_input("Toneladas Porão 1", min_value=0, step=50, value=val_p1, key=f"p1_{turno_atual}")
        with col3: v2 = st.number_input("Toneladas Porão 2", min_value=0, step=50, value=val_p2, key=f"p2_{turno_atual}")
        with col4: v3 = st.number_input("Toneladas Porão 3", min_value=0, step=50, value=val_p3, key=f"p3_{turno_atual}")
        with col5: v4 = st.number_input("Toneladas Porão 4", min_value=0, step=50, value=val_p4, key=f"p4_{turno_atual}")
        
        c_btn1, c_btn2 = st.columns([4, 1])
        with c_btn1:
            if st.button(texto_botao, use_container_width=True, key=f"btn_salvar_{turno_atual}"):
                hora_atual = datetime.now().strftime("%H:%M:%S")
                usuario_ativo = st.session_state.user_name
                
                if st.session_state.edit_mode:
                    st.session_state[chave_tabela].at[st.session_state.edit_index, "Dia"] = data_lan.strftime("%d/%m/%Y")
                    st.session_state[chave_tabela].at[st.session_state.edit_index, "Porão 1"] = v1
                    st.session_state[chave_tabela].at[st.session_state.edit_index, "Porão 2"] = v2
                    st.session_state[chave_tabela].at[st.session_state.edit_index, "Porão 3"] = v3
                    st.session_state[chave_tabela].at[st.session_state.edit_index, "Porão 4"] = v4
                    st.session_state[chave_tabela].at[st.session_state.edit_index, "Saldo"] = v1+v2+v3+v4
                    st.session_state[chave_tabela].at[st.session_state.edit_index, "Usuario"] = usuario_ativo
                    st.session_state[chave_tabela].at[st.session_state.edit_index, "Hora"] = hora_atual
                    st.session_state.edit_mode, st.session_state.edit_index = False, None
                else:
                    nova = pd.DataFrame([{
                        "Dia": data_lan.strftime("%d/%m/%Y"), 
                        "Porão 1": v1, "Porão 2": v2, "Porão 3": v3, "Porão 4": v4, 
                        "Saldo": v1+v2+v3+v4,
                        "Usuario": usuario_ativo,
                        "Hora": hora_atual
                    }])
                    st.session_state[chave_tabela] = pd.concat([df_atual, nova], ignore_index=True)
                st.rerun()
        with c_btn2:
            if st.session_state.edit_mode and st.button("Cancelar", use_container_width=True):
                st.session_state.edit_mode, st.session_state.edit_index = False, None
                st.rerun()

    if not df_atual.empty:
        st.markdown("#### Lançamentos Registrados")
        cols_headers = st.columns([2, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1])
        headers = ["Dia", "Porão 1", "Porão 2", "Porão 3", "Porão 4", "Saldo", "Usuário", "Ação"]
        for i, h in enumerate(headers): cols_headers[i].markdown(f"<th>{h}</th>", unsafe_allow_html=True)
            
        for idx, row in df_atual.iterrows():
            cols_row = st.columns([2, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1])
            cols_row[0].markdown(f"<td>{row['Dia']}</td>", unsafe_allow_html=True)
            cols_row[1].markdown(f"<td>{row['Porão 1']} t</td>", unsafe_allow_html=True)
            cols_row[2].markdown(f"<td>{row['Porão 2']} t</td>", unsafe_allow_html=True)
            cols_row[3].markdown(f"<td>{row['Porão 3']} t</td>", unsafe_allow_html=True)
            cols_row[4].markdown(f"<td>{row['Porão 4']} t</td>", unsafe_allow_html=True)
            cols_row[5].markdown(f"<td>{row['Saldo']} t</td>", unsafe_allow_html=True)
            cols_row[6].markdown(f"<td>{row.get('Usuario', '-')}</td>", unsafe_allow_html=True)
            if cols_row[7].button("✏️", key=f"edit_{idx}"):
                st.session_state.edit_mode, st.session_state.edit_index = True, idx
                st.rerun()

        st.markdown("---")
        df_calculo = df_atual.copy()
        df_calculo[["Porão 1", "Porão 2", "Porão 3", "Porão 4", "Saldo"]] = df_calculo[["Porão 1", "Porão 2", "Porão 3", "Porão 4", "Saldo"]].apply(pd.to_numeric).fillna(0)
        
        cols_total = st.columns([2, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1])
        cols_total[0].markdown("<th>TOTAL TURNO</th>", unsafe_allow_html=True)
        cols_total[1].markdown(f"<td>{int(df_calculo['Porão 1'].sum())} t</td>", unsafe_allow_html=True)
        cols_total[2].markdown(f"<td>{int(df_calculo['Porão 2'].sum())} t</td>", unsafe_allow_html=True)
        cols_total[3].markdown(f"<td>{int(df_calculo['Porão 3'].sum())} t</td>", unsafe_allow_html=True)
        cols_total[4].markdown(f"<td>{int(df_calculo['Porão 4'].sum())} t</td>", unsafe_allow_html=True)
        cols_total[5].markdown(f"<td>{int(df_calculo['Saldo'].sum())} t</td>", unsafe_allow_html=True)
    else:
        st.info("Nenhum registro lançado para este turno.")

# =====================================================================
# MÓDULO 1: CADASTRO INTERNO (RESTRITO AO ADMINISTRADOR)
# =====================================================================
def bloco_cadastro():
    st.markdown("<h2>👥 Cadastrar Novo Operador</h2>", unsafe_allow_html=True)
    st.markdown('<div class="custom-box">', unsafe_allow_html=True)
    nu = st.text_input("Definir Usuário")
    np = st.text_input("Definir Senha", type="password")
    nt = st.selectbox("Vincular a qual Turno Fixo?", ["1º TURNO", "2º TURNO"])
    if st.button("Salvar Operador no Banco", use_container_width=True):
        st.session_state.banco_usuarios[nu] = {"senha": np, "turno_fixo": nt, "role": "operador"}
        st.success(f"Operador '{nu}' cadastrado com sucesso para o {nt}!")
    st.markdown('</div>', unsafe_allow_html=True)

# =====================================================================
# INTERFACE DE LOGIN DE ACESSO
# =====================================================================
def bloco_login():
    st.markdown('<div class="custom-box">', unsafe_allow_html=True)
    st.title("Zion Tecnologia")
    st.subheader("Login de Acesso")
    u = st.text_input("Nome de Usuário")
    p = st.text_input("Senha do Sistema", type="password")
    
    if st.button("Entrar no Sistema", use_container_width=True):
        banco = st.session_state.banco_usuarios
        if u in banco and banco[u]["senha"] == p:
            st.session_state.logged_in = True
            st.session_state.user_name = u
            st.session_state.role = banco[u]["role"]
            
            if banco[u]["role"] == "admin":
                st.session_state.turno_trabalho = "1º TURNO"
            else:
                st.session_state.turno_trabalho = banco[u]["turno_fixo"]
                
            st.session_state.menu_atual = "Lançamentos"
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos.")
    st.markdown('</div>', unsafe_allow_html=True)

# =====================================================================
# ORQUESTRADOR CENTRAL (CONTROLE DE MENUS E NÍVEIS DE ACESSO)
# =====================================================================
def main():
    aplicar_estilo_visual()
    inicializar_dados()

    if st.session_state.logged_in:
        st.sidebar.title("Zion Operações")
        st.sidebar.markdown(f"**Usuário:** {st.session_state.user_name} ({st.session_state.role.upper()})")
        
        if st.session_state.role == "admin":
            st.session_state.turno_trabalho = st.sidebar.selectbox(
                "Visualizar Qual Turno?", 
                ["1º TURNO", "2º TURNO"], 
                index=0 if st.session_state.turno_trabalho == "1º TURNO" else 1
            )
        else:
            st.sidebar.markdown(f"**Turno Ativo:** {st.session_state.turno_trabalho}")
            
        st.sidebar.markdown("---")
        
        if st.sidebar.button("📋 Lançamentos do Turno", use_container_width=True):
            st.session_state.menu_atual = "Lançamentos"
            st.rerun()
            
        if st.session_state.role == "admin":
            if st.sidebar.button("📊 Global (Consolidado)", use_container_width=True):
                st.session_state.menu_atual = "Global"
                st.rerun()
            if st.sidebar.button("👤 Cadastrar Operador", use_container_width=True):
                st.session_state.menu_atual = "Cadastro"
                st.rerun()
                
        st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
        if st.sidebar.button("🚪 Sair do Sistema", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
            
        if st.session_state.menu_atual == "Lançamentos":
            bloco_painel_poroes(st.session_state.turno_trabalho)
        elif st.session_state.menu_atual == "Global" and st.session_state.role == "admin":
            bloco_consolidado_geral()
        elif st.session_state.menu_atual == "Cadastro" and st.session_state.role == "admin":
            bloco_cadastro()
    else:
        bloco_login()

if __name__ == "__main__":
    main()
