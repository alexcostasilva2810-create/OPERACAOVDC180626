import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from streamlit_gsheets import GSheetsConnection

# =====================================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================================
st.set_page_config(page_title="Zion Tecnologia - Gestão Portuária", page_icon="🚢", layout="wide")

# =====================================================================
# BLOCO: ESTILIZAÇÃO VISUAL (CSS DE ALTO CONTRASTE)
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
# BLOCO: BANCO DE DADOS EM MEMÓRIA E ATUALIZADOR DO GOOGLE SHEETS
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

    colunas = ["Dia", "Porão 1", "Porão 2", "Porão 3", "Porão 4", "Porão 5", "Saldo", "Usuario", "Hora"]
    if 'tabela_turno_1' not in st.session_state:
        st.session_state.tabela_turno_1 = pd.DataFrame(columns=colunas)
    if 'tabela_turno_2' not in st.session_state:
        st.session_state.tabela_turno_2 = pd.DataFrame(columns=colunas)
        
    if 'edit_mode' not in st.session_state: st.session_state.edit_mode = False
    if 'edit_index' not in st.session_state: st.session_state.edit_index = None

def sincronizar_visao_global_com_sheets(df_global_atual):
    """Envia a tabela pronta e formatada exatamente para a aba Global do Sheets"""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_salvar = df_global_atual.copy()
        df_salvar.columns = ["Turno", "Dia", "Porão 1", "Porão 2", "Porão 3", "Porão 4", "Porão 5", "Saldo", "Usuário", "Hora do Registro"]
        conn.update(worksheet="Global", data=df_salvar)
    except Exception as e:
        st.error(f"Aviso: Não foi possível atualizar a planilha Google: {e}")

def obter_df_combinado():
    df1 = st.session_state.tabela_turno_1.copy()
    df1["Turno"] = "1º TURNO"
    df2 = st.session_state.tabela_turno_2.copy()
    df2["Turno"] = "2º TURNO"
    df_combinado = pd.concat([df1, df2], ignore_index=True)
    
    ordem_colunas = ["Turno", "Dia", "Porão 1", "Porão 2", "Porão 3", "Porão 4", "Porão 5", "Saldo", "Usuario", "Hora"]
    if not df_combinado.empty:
        return df_combinado[ordem_colunas]
    return pd.DataFrame(columns=ordem_colunas)

# =====================================================================
# REPORTLAB: GERADOR DO RELATÓRIO PDF CONSOLIDADO
# =====================================================================
def gerar_pdf_reportlab(p1, p2, p3, p4, p5, saldo, df_combinado):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=20, leftMargin=20, topMargin=40, bottomMargin=40)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#0f172a'), alignment=1, spaceAfter=20)
    heading_style = ParagraphStyle('HeadingStyle', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#0284c7'), spaceBefore=15, spaceAfter=10)
    normal_style = ParagraphStyle('NormalStyle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#1e293b'))

    story.append(Paragraph("Relatório Consolidado de Carregamento - Global", title_style))
    story.append(Paragraph("<b>Zion Tecnologia</b> — Sistema de Controle Portuário Integrado", normal_style))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("Resumo Acumulado por Porão", heading_style))
    dados_resumo = [['Porão 1', 'Porão 2', 'Porão 3', 'Porão 4', 'Porão 5', 'SALDO GLOBAL'], [f"{p1} t", f"{p2} t", f"{p3} t", f"{p4} t", f"{p5} t", f"{saldo} t"]]
    t_resumo = Table(dados_resumo, colWidths=[90, 90, 90, 90, 90, 110])
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
    dados_tabela = [['Turno', 'Data', 'Porão 1', 'Porão 2', 'Porão 3', 'Porão 4', 'Porão 5', 'Saldo', 'Usuário', 'Hora']]
    
    for _, row in df_combinado.iterrows():
        usr = str(row.get('Usuario', '-'))
        hra = str(row.get('Hora', '-'))
        dados_tabela.append([
            str(row['Turno']), str(row['Dia']), 
            f"{int(row['Porão 1'])} t", f"{int(row['Porão 2'])} t", 
            f"{int(row['Porão 3'])} t", f"{int(row['Porão 4'])} t", f"{int(row['Porão 5'])} t", 
            f"{int(row['Saldo'])} t", usr, hra
        ])
    
    t_dados = Table(dados_tabela, colWidths=[60, 60, 50, 50, 50, 50, 50, 55, 75, 55])
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
    col_tit_1, col_tit_2, col_tit_3 = st.columns([1, 4, 1])
    with col_tit_2:
        st.markdown("<h2 style='text-align: center; color: #38bdf8 !important;'>Painel Gerencial Global (Turno 1 + Turno 2)</h2>", unsafe_allow_html=True)
    
    df_combinado = obter_df_combinado()
    
    df1 = st.session_state.tabela_turno_1
    df2 = st.session_state.tabela_turno_2
    
    p1_total = pd.to_numeric(df1["Porão 1"]).sum() if not df1.empty else 0
    p1_total += pd.to_numeric(df2["Porão 1"]).sum() if not df2.empty else 0
    
    p2_total = pd.to_numeric(df1["Porão 2"]).sum() if not df1.empty else 0
    p2_total += pd.to_numeric(df2["Porão 2"]).sum() if not df2.empty else 0
    
    p3_total = pd.to_numeric(df1["Porão 3"]).sum() if not df1.empty else 0
    p3_total += pd.to_numeric(df2["Porão 3"]).sum() if not df2.empty else 0
    
    p4_total = pd.to_numeric(df1["Porão 4"]).sum() if not df1.empty else 0
    p4_total += pd.to_numeric(df2["Porão 4"]).sum() if not df2.empty else 0

    p5_total = pd.to_numeric(df1["Porão 5"]).sum() if not df1.empty else 0
    p5_total += pd.to_numeric(df2["Porão 5"]).sum() if not df2.empty else 0
    
    saldo_geral = p1_total + p2_total + p3_total + p4_total + p5_total
    meta_referencia = 50000
    falta_atingir = meta_referencia - saldo_geral if (meta_referencia - saldo_geral) > 0 else 0

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total Porão 1", f"{int(p1_total)} t")
    c2.metric("Total Porão 2", f"{int(p2_total)} t")
    c3.metric("Total Porão 3", f"{int(p3_total)} t")
    c4.metric("Total Porão 4", f"{int(p4_total)} t")
    c5.metric("Total Porão 5", f"{int(p5_total)} t")
    c6.metric("TOTAL LANÇADO", f"{int(saldo_geral)} t")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    meta_col1, meta_col2 = st.columns(2)
    with meta_col1: st.metric("REFERÊNCIA CONTRATUAL", f"{meta_referencia} t")
    with meta_col2: st.metric("QUANTO FALTA ATINGIR", f"{int(falta_atingir)} t")

    st.markdown("---")
    st.markdown("#### Histórico de Todos os Lançamentos Realizados")
    
    if not df_combinado.empty:
        df_combinado[["Porão 1", "Porão 2", "Porão 3", "Porão 4", "Porão 5", "Saldo"]] = df_combinado[["Porão 1", "Porão 2", "Porão 3", "Porão 4", "Porão 5", "Saldo"]].apply(pd.to_numeric).fillna(0)
        
        cols_headers
