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
        
    # Controle do Estado de Edição
    if 'edit_mode' not in st.session_state: st.session_state.edit_mode = False
    if 'edit_index' not in st.session_state: st.session_state.edit_index = None

# =====================================================================
# FUNÇÃO AUXILIAR: GERADOR DE PDF USANDO REPORTLAB (NATIVO E SEGURO)
# =====================================================================
def gerar_pdf_reportlab(p1, p2, p3, p4, saldo, df_combinado):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    
    styles = getSampleStyleSheet()
    
    # Customização de estilos
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#0f172a'),
        alignment=1, # Centralizado
        spaceAfter=20
    )
    
    heading_style = ParagraphStyle(
        'HeadingStyle',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#0284c7'),
        spaceBefore=15,
        spaceAfter=10
    )
    
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#1e293b')
    )

    # 1. Cabeçalho Principal
    story.append(Paragraph("Relatório Consolidado de carregamento", title_style))
    story.append(Paragraph("<b>Zion Tecnologia</b> — Sistema de Controle Portuário Integrado", normal_style))
    story.append(Spacer(1, 15))
    
    # 2. Quadro Informativo de Totais por Porão
    story.append(Paragraph("Resumo Acumulado por Porão", heading_style))
    dados_resumo = [
        ['Porão 1', 'Porão 2', 'Porão 3', 'Porão 4', 'SALDO GLOBAL'],
        [f"{p1} t", f"{p2} t", f"{p3} t", f"{p4} t", f"{saldo} t"]
    ]
    t_resumo = Table(dados_resumo, colWidths=[100, 100, 100, 100, 120])
    t_resumo.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#f8fafc')),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('FONTSIZE', (0,0), (-1,-1), 10),
    ]))
    story.append(t_resumo)
    story.append(Spacer(1, 20))
    
    # 3. Tabela Histórica Completa
    story.append(Paragraph("Demonstrativo Detalhado de Movimentações", heading_style))
    
    dados_tabela = [['Data da Operação', 'Porão 1 (t)', 'Porão 2 (t)', 'Porão 3 (t)', 'Porão 4 (t)', 'Saldo Diário (t)']]
    for _, row in df_combinado.iterrows():
        dados_tabela.append([
            str(row['Dia']),
            str(int(row['Porão 1'])),
            str(int(row['Porão 2'])),
            str(int(row['Porão 3'])),
            str(int(row['Porão 4'])),
            str(int(row['Saldo']))
        ])
    
    # Linha final de totais consolidada
    dados_tabela.append(['TOTAL CONSOLIDADO', str(int(p1)), str(int(p2)), str(int(p3)), str(int(p4)), str(int(saldo))])
    
    t_dados = Table(dados_tabela, colWidths=[120, 80, 80, 80, 80, 100])
    t_dados.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e293b')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('BACKGROUND', (0,1), (-1,-2), colors.white),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor('#f8fafc')]),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#cbd5e1')),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
    ]))
    story.append(t_dados)
    
    # Construção do documento
    doc.build(story)
    return buffer.getvalue()

# =====================================================================
# MÓDULO 3: VISÃO CONSOLIDADA COM RELATÓRIO PDF EM REPORTLAB
# =====================================================================
def bloco_consolidado_geral():
    st.markdown("## 🌍 Painel Gerencial Consolidado (Turno 1 + Turno 2)")
    
    df1 = st.session_state.tabela_turno_1.copy()
    df2 = st.session_state.tabela_turno_2.copy()
    
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
        # Exibição limpa estruturada em HTML nativo para o CSS respeitar a cor verde viva
        html_table = "<table><thead><tr><th>Dia</th><th>Porão 1</th><th>Porão 2</th><th>Porão 3</th><th>Porão 4</th><th>Saldo</th></tr></thead><tbody>"
        for _, r in df_combinado.iterrows():
            html_table += f"<tr><td>{r['Dia']}</td><td>{r['Porão 1']}</td><td>{r['Porão 2']}</td><td>{r['Porão 3']}</td><td>{r['Porão 4']}</td><td>{r['Saldo']}</td></tr>"
        html_table += "</tbody></table>"
        st.markdown(html_table, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Geração em Tempo Real do arquivo PDF via ReportLab
        pdf_data = gerar_pdf_reportlab(p1_total, p2_total, p3_total, p4_total, saldo_geral, df_combinado)
        
        st.download_button(
            label="📥 Exportar Relatório em PDF",
            data=pdf_data,
            file_name="Relatorio_Consolidado_Carregamento.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.info("Aguardando lançamentos dos turnos para consolidar os relatórios.")

# =====================================================================
# MÓDULO 2: LANÇAMENTOS COM SISTEMA DE EDIÇÃO DE LINHAS INTEGRADO
# =====================================================================
def bloco_painel_poroes(turno_atual):
    st.markdown(f"### 📊 Lançamentos Atuais - {turno_atual}")
    chave_tabela = 'tabela_turno_1' if turno_atual == "1º TURNO" else 'tabela_turno_2'
    df_atual = st.session_state[chave_tabela]

    # Estado Padrão dos Inputs para Criação ou Carregamento para Edição
    if st.session_state.edit_mode and st.session_state.edit_index is not None:
        row_edit = df_atual.iloc[st.session_state.edit_index]
        titulo_box = "✏️ Alterar Dados e Salvar Registro"
        texto_botao = "💾 Salvar Alterações"
        val_p1 = int(row_edit["Porão 1"])
        val_p2 = int(row_edit["Porão 2"])
        val_p3 = int(row_edit["Porão 3"])
        val_p4 = int(row_edit["Porão 4"])
    else:
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
                if st.session_state.edit_mode:
                    # Sobrescreve a linha editada antiga
                    st.session_state[chave_tabela].at[st.session_state.edit_index, "Dia"] = data_lan.strftime("%d/%m/%Y")
                    st.session_state[chave_tabela].at[st.session_state.edit_index, "Porão 1"] = v1
                    st.session_state[chave_tabela].at[st.session_state.edit_index, "Porão 2"] = v2
                    st.session_state[chave_tabela].at[st.session_state.edit_index, "Porão 3"] = v3
                    st.session_state[chave_tabela].at[st.session_state.edit_index, "Porão 4"] = v4
                    st.session_state[chave_tabela].at[st.session_state.edit_index, "Saldo"] = v1+v2+v3+v4
                    st.session_state.edit_mode = False
                    st.session_state.edit_index = None
                    st.success("Alteração gravada com sucesso!")
                else:
                    # Cria um novo registro comum
                    nova = pd.DataFrame([{"Dia": data_lan.strftime("%d/%m/%Y"), "Porão 1": v1, "Porão 2": v2, "Porão 3": v3, "Porão 4": v4, "Saldo": v1+v2+v3+v4}])
                    st.session_state[chave_tabela] = pd.concat([df_atual, nova], ignore_index=True)
                    st.success("Dados gravados com sucesso!")
                st.rerun()
        with c_btn2:
            if st.session_state.edit_mode:
                if st.button("Cancelar", use_container_width=True):
                    st.session_state.edit_mode = False
                    st.session_state.edit_index = None
                    st.rerun()

    # Tabela com Controle Customizado de Edição por Linha
    if not df_atual.empty:
        st.markdown("#### Lançamentos Registrados")
        
        # Construção da cabeçalho da tabela
        cols_headers = st.columns([2, 2, 2, 2, 2, 2, 2])
        headers = ["Dia", "Porão 1", "Porão 2", "Porão 3", "Porão 4", "Saldo", "Ação"]
        for i, h in enumerate(headers):
            cols_headers[i].markdown(f"<th>{h}</th>", unsafe_allow_html=True)
            
        # Renderização dinâmica linha por linha
        for idx, row in df_atual.iterrows():
            cols_row = st.columns([2, 2, 2, 2, 2, 2, 2])
            cols_row[0].markdown(f"<td>{row['Dia']}</td>", unsafe_allow_html=True)
            cols_row[1].markdown(f"<td>{row['Porão 1']} t</td>", unsafe_allow_html=True)
            cols_row[2].markdown(f"<td>{row['Porão 2']} t</td>", unsafe_allow_html=True)
            cols_row[3].markdown(f"<td>{row['Porão 3']} t</td>", unsafe_allow_html=True)
            cols_row[4].markdown(f"<td>{row['Porão 4']} t</td>", unsafe_allow_html=True)
            cols_row[5].markdown(f"<td>{row['Saldo']} t</td>", unsafe_allow_html=True)
            
            if cols_row[6].button("✏️ Editar", key=f"edit_{idx}"):
                st.session_state.edit_mode = True
                st.session_state.edit_index = idx
                st.rerun()

        # Linha de Totais do Turno
        st.markdown("---")
        df_atual[["Porão 1", "Porão 2", "Porão 3", "Porão 4", "Saldo"]] = df_atual[["Porão 1", "Porão 2", "Porão 3", "Porão 4", "Saldo"]].apply(pd.to_numeric)
        cols_total = st.columns([2, 2, 2, 2, 2, 2, 2])
        cols_total[0].markdown("<th>TOTAL TURNO</th>", unsafe_allow_html=True)
        cols_total[1].markdown(f"<td>{df_atual['Porão 1'].sum()} t</td>", unsafe_allow_html=True)
        cols_total[2].markdown(f"<td>{df_atual['Porão 2'].sum()} t</td>", unsafe_allow_html=True)
        cols_total[3].markdown(f"<td>{df_atual['Porão 3'].sum()} t</td>", unsafe_allow_html=True)
        cols_total[4].markdown(f"<td>{df_atual['Porão 4'].sum()} t</td>", unsafe_allow_html=True)
        cols_total[5].markdown(f"<td>{df_atual['Saldo'].sum()} t</td>", unsafe_allow_html=True)
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
