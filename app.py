import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from streamlit_gsheets import GSheetsConnection

# Configuração da página
st.set_page_config(page_title="Zion Tecnologia - Gestão Portuária", page_icon="🚢", layout="wide")

# 1. INICIALIZAÇÃO DO BANCO DE USUÁRIOS
if 'banco_usuarios' not in st.session_state:
    st.session_state.banco_usuarios = {
        "admin": {"senha": "1234", "role": "admin"},
        "admin2": {"senha": "5678", "role": "admin"},
        "alex": {"senha": "zion2026", "turno_fixo": "1º TURNO", "role": "operador"},
        "Rubens Ferreira": {"senha": "8036", "turno_fixo": "2º TURNO", "role": "operador"}
    }

# FUNÇÃO PARA PEGAR A HORA ATUAL DO BRASIL
def obtener_hora_atual_brasil():
    hora_local = datetime.utcnow() - timedelta(hours=3)
    return hora_local.strftime("%H:%M:%S")

# 2. ESTILIZAÇÃO CSS COMPLETA (SEM O RETÂNGULO VAZIO NO LOGIN)
st.markdown(
    """
    <style>
    /* TODO O SISTEMA: Fundo preto */
    .stApp, [data-testid="stSidebar"] { 
        background-color: #000000 !important; 
    }
    
    /* Textos do sistema em verde */
    p, label, .stMarkdown p, .stSelectbox label, .stInputField label, .stDateInput label { 
        color: #00ff66 !important; 
        font-weight: bold !important; 
    }
    h1, h2, h3, h4 { color: #00ff66 !important; font-weight: bold !important; }
    
    /* Título ZION Elegante no Topo */
    .zion-header {
        text-align: center;
        font-family: 'Helvetica Neue', sans-serif;
        font-size: 55px;
        font-weight: 900;
        letter-spacing: 10px;
        color: #00ff66;
        margin-top: 3rem;
        margin-bottom: 0px;
    }
    
    .zion-subtitle {
        text-align: center;
        font-size: 13px;
        letter-spacing: 4px;
        color: #00ff66;
        margin-top: 0px;
        margin-bottom: 2.5rem;
        text-transform: uppercase;
        opacity: 0.8;
    }

    /* Container customizado do Login */
    .login-container {
        border: 2px solid #00ff66;
        border-radius: 12px;
        padding: 25px;
        background-color: #000000;
    }

    /* Letras de todos os botões do menu lateral em PRETO */
    [data-testid="stSidebar"] button p {
        color: #000000 !important;
        font-weight: bold !important;
    }
    
    /* Estilo do botão de navegação lateral (Fundo Branco) */
    [data-testid="stSidebar"] button {
        background-color: #ffffff !important;
        border: 1px solid #00ff66 !important;
    }

    /* Tabelas e Editores (Fundo branco, letras pretas e CENTRALIZADO) */
    .tabela-global-exclusiva td, .tabela-global-exclusiva th, .tabela-global-exclusiva p, .tabela-global-exclusiva span {
        color: #000000 !important;
        font-weight: normal !important;
        text-align: center !important;
    }
    [data-testid="stTable"] td, [data-testid="stDataFrame"] td, [data-testid="stDataEditor"] td {
        text-align: center !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'turno_trabalho' not in st.session_state: st.session_state.turno_trabalho = "1º TURNO"
if 'role' not in st.session_state: st.session_state.role = "operador"
if 'menu_atual' not in st.session_state: st.session_state.menu_atual = "Lançamentos"

colunas = ["Dia", "Porão 1", "Porão 2", "Porão 3", "Porão 4", "Porão 5", "Saldo", "Usuario", "Hora"]
if 'tabela_turno_1' not in st.session_state: st.session_state.tabela_turno_1 = pd.DataFrame(columns=colunas)
if 'tabela_turno_2' not in st.session_state: st.session_state.tabela_turno_2 = pd.DataFrame(columns=colunas)
if 'edit_mode' not in st.session_state: st.session_state.edit_mode = False
if 'edit_index' not in st.session_state: st.session_state.edit_index = None

def sincronizar_visao_global_com_sheets(df_global_atual):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_salvar = df_global_atual.copy()
        df_salvar.columns = ["Turno", "Dia", "Porão 1", "Porão 2", "Porão 3", "Porão 4", "Porão 5", "Saldo", "Usuário", "Hora do Registro"]
        conn.update(worksheet="Global", data=df_salvar)
        st.cache_data.clear()
    except Exception:
        pass

def obter_df_combinado():
    df1 = st.session_state.tabela_turno_1.copy()
    df1["Turno"] = "1º TURNO"
    df1["orig_index"] = df1.index
    
    df2 = st.session_state.tabela_turno_2.copy()
    df2["Turno"] = "2º TURNO"
    df2["orig_index"] = df2.index
    
    df_combinado = pd.concat([df1, df2], ignore_index=True)
    ordem_colunas = ["Turno", "Dia", "Porão 1", "Porão 2", "Porão 3", "Porão 4", "Porão 5", "Saldo", "Usuario", "Hora", "orig_index"]
    if not df_combinado.empty:
        return df_combinado[ordem_colunas]
    return pd.DataFrame(columns=ordem_colunas)

def gerar_pdf_reportlab(p1, p2, p3, p4, p5, saldo, df_combinado):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=20, leftMargin=20, topMargin=40, bottomMargin=40)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('T1', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#0f172a'), alignment=1, spaceAfter=15)
    normal_style = ParagraphStyle('N', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#1e293b'))

    story.append(Paragraph("Relatório Consolidado de Carregamento - Global", title_style))
    story.append(Paragraph("<b>Zion Tecnologia</b> — Sistema de Controle Portuário", normal_style))
    story.append(Spacer(1, 15))
    
    dados_resumo = [['Porão 1', 'Porão 2', 'Porão 3', 'Porão 4', 'Porão 5', 'TOTAL NAVIO'], [f"{p1} t", f"{p2} t", f"{p3} t", f"{p4} t", f"{p5} t", f"{saldo} t"]]
    t_resumo = Table(dados_resumo, colWidths=[85, 85, 85, 85, 85, 100])
    t_resumo.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
    ]))
    story.append(t_resumo)
    story.append(Spacer(1, 15))
    
    dados_tabela = [['Turno', 'Data', 'P1', 'P2', 'P3', 'P4', 'P5', 'Saldo', 'Usuário', 'Hora']]
    for _, row in df_combinado.iterrows():
        dados_tabela.append([
            str(row['Turno']), str(row['Dia']), f"{int(row['Porão 1'])} t", f"{int(row['Porão 2'])} t", 
            f"{int(row['Porão 3'])} t", f"{int(row['Porão 4'])} t", f"{int(row['Porão 5'])} t", 
            f"{int(row['Saldo'])} t", str(row.get('Usuario', '-')), str(row.get('Hora', '-'))
        ])
    
    t_dados = Table(dados_tabela, colWidths=[65, 55, 45, 45, 45, 45, 45, 50, 75, 50])
    t_dados.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e293b')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
    ]))
    story.append(t_dados)
    doc.build(story)
    return buffer.getvalue()

def bloco_consolidado_geral():
    st.markdown("<h2 style='text-align: center;'>Painel Gerencial Global (5 Porões)</h2>", unsafe_allow_html=True)
    df_combinado = obter_df_combinado()
    
    df1, df2 = st.session_state.tabela_turno_1, st.session_state.tabela_turno_2
    
    p1 = pd.to_numeric(df1["Porão 1"]).sum() + pd.to_numeric(df2["Porão 1"]).sum() if not (df1.empty and df2.empty) else 0
    p2 = pd.to_numeric(df1["Porão 2"]).sum() + pd.to_numeric(df2["Porão 2"]).sum() if not (df1.empty and df2.empty) else 0
    p3 = pd.to_numeric(df1["Porão 3"]).sum() + pd.to_numeric(df2["Porão 3"]).sum() if not (df1.empty and df2.empty) else 0
    p4 = pd.to_numeric(df1["Porão 4"]).sum() + pd.to_numeric(df2["Porão 4"]).sum() if not (df1.empty and df2.empty) else 0
    p5 = pd.to_numeric(df1["Porão 5"]).sum() + pd.to_numeric(df2["Porão 5"]).sum() if not (df1.empty and df2.empty) else 0
    
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
    
    meta_col1, meta_col2 = st.columns(2)
    with meta_col1: st.metric("REFERÊNCIA CONTRATUAL", f"{meta_referencia} t")
    with meta_col2: st.metric("QUANTO FALTA ATINGIR", f"{int(falta_atingir)} t")

    st.markdown("---")
    st.markdown("#### Histórico de Lançamentos Realizados")
    st.caption("💡 Para excluir: Selecione o quadradinho na esquerda da linha e aperte a lixeira da tabela ou a tecla Delete.")
    
    if not df_combinado.empty:
        df_visual = df_combinado.drop(columns=["orig_index"])
        df_estilizado = df_visual.style.set_properties(**{'text-align': 'center'})
        
        st.markdown('<div class="tabela-global-exclusiva">', unsafe_allow_html=True)
        linhas_editadas = st.data_editor(
            df_estilizado, 
            use_container_width=True, 
            hide_index=True,
            num_rows="dynamic",
            disabled=["Turno", "Dia", "Porão 1", "Porão 2", "Porão 3", "Porão 4", "Porão 5", "Saldo", "Usuario", "Hora"]
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        if len(linhas_editadas) < len(df_visual):
            indices_mantidos = linhas_editadas.index.tolist()
            df_removidos = df_combinado[~df_combinado.index.isin(indices_mantidos)]
            
            for _, row in df_removidos.iterrows():
                t_alvo = row["Turno"]
                orig_idx = row["orig_index"]
                if t_alvo == "1º TURNO":
                    st.session_state.tabela_turno_1 = st.session_state.tabela_turno_1.drop(orig_idx).reset_index(drop=True)
                else:
                    st.session_state.tabela_turno_2 = st.session_state.tabela_turno_2.drop(orig_idx).reset_index(drop=True)
            
            df_atualizado = obter_df_combinado()
            if not df_atualizado.empty:
                df_atualizado = df_atualizado.drop(columns=["orig_index"])
            sincronizar_visao_global_com_sheets(df_atualizado)
            st.rerun()
        
        st.markdown("---")
        pdf_data = gerar_pdf_reportlab(p1, p2, p3, p4, p5, saldo_geral, df_combinado.drop(columns=["orig_index"]))
        st.download_button(
            label="Exportar Relatório Global em PDF", data=pdf_data,
            file_name="Relatorio_Global_Carregamento.pdf", mime="application/pdf", use_container_width=True
        )
    else:
        st.info("Nenhum dado lançado nos turnos até o momento.")

def bloco_painel_poroes(turno_atual):
    st.markdown(f"<h2>Lançamentos Atuais - {turno_atual}</h2>", unsafe_allow_html=True)
    chave_tabela = 'tabela_turno_1' if turno_atual == "1º TURNO" else 'tabela_turno_2'
    df_atual = st.session_state[chave_tabela]

    if st.session_state.edit_mode and st.session_state.edit_index is not None:
        row_edit = df_atual.iloc[st.session_state.edit_index]
        val_p1 = int(row_edit["Porão 1"])
        val_p2 = int(row_edit["Porão 2"])
        val_p3 = int(row_edit["Porão 3"])
        val_p4 = int(row_edit["Porão 4"])
        val_p5 = int(row_edit["Porão 5"])
        titulo_box, texto_botao = "Alterar Lançamento", "Salvar Alterações"
    else:
        val_p1 = val_p2 = val_p3 = val_p4 = val_p5 = 0
        titulo_box, texto_botao = "Novo Lançamento (5 Porões)", "Gravar Lançamento"

    with st.expander(titulo_box, expanded=True):
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1: data_lan = st.date_input("Data", format="DD/MM/YYYY", key=f"dt_{turno_atual}")
        with col2: v1 = st.number_input("Porão 1 (t)", min_value=0, step=50, value=val_p1, key=f"p1_{turno_atual}")
        with col3: v2 = st.number_input("Porão 2 (t)", min_value=0, step=50, value=val_p2, key=f"p2_{turno_atual}")
        with col4: v3 = st.number_input("Porão 3 (t)", min_value=0, step=50, value=val_p3, key=f"p3_{turno_atual}")
        with col5: v4 = st.number_input("Porão 4 (t)", min_value=0, step=50, value=val_p4, key=f"p4_{turno_atual}")
        with col6: v5 = st.number_input("Porão 5 (t)", min_value=0, step=50, value=val_p5, key=f"p5_{turno_atual}")
        
        c_btn1, c_btn2 = st.columns([5, 1])
        with c_btn1:
            if st.button(texto_botao, use_container_width=True):
                hora_correta = obter_hora_atual_brasil()
                
                if st.session_state.edit_mode:
                    idx = st.session_state.edit_index
                    st.session_state[chave_tabela].at[idx, "Dia"] = data_lan.strftime("%d/%m/%Y")
                    st.session_state[chave_tabela].at[idx, "Porão 1"] = v1
                    st.session_state[chave_tabela].at[idx, "Porão 2"] = v2
                    st.session_state[chave_tabela].at[idx, "Porão 3"] = v3
                    st.session_state[chave_tabela].at[idx, "Porão 4"] = v4
                    st.session_state[chave_tabela].at[idx, "Porão 5"] = v5
                    st.session_state[chave_tabela].at[idx, "Saldo"] = v1+v2+v3+v4+v5
                    st.session_state[chave_tabela].at[idx, "Usuario"] = st.session_state.user_name
                    st.session_state[chave_tabela].at[idx, "Hora"] = hora_correta
                    st.session_state.edit_mode, st.session_state.edit_index = False, None
                else:
                    nova = pd.DataFrame([{"Dia": data_lan.strftime("%d/%m/%Y"), "Porão 1": v1, "Porão 2": v2, "Porão 3": v3, "Porão 4": v4, "Porão 5": v5, "Saldo": v1+v2+v3+v4+v5, "Usuario": st.session_state.user_name, "Hora": hora_correta}])
                    st.session_state[chave_tabela] = pd.concat([df_atual, nova], ignore_index=True)
                
                df_sheets_atualizado = obter_df_combinado()
                if not df_sheets_atualizado.empty:
                    df_sheets_atualizado = df_sheets_atualizado.drop(columns=["orig_index"])
                sincronizar_visao_global_com_sheets(df_sheets_atualizado)
                st.rerun()
        with c_btn2:
            if st.session_state.edit_mode and st.button("Cancelar", use_container_width=True):
                st.session_state.edit_mode, st.session_state.edit_index = False, None
                st.rerun()

    if not df_atual.empty:
        st.markdown("#### Histórico do Turno")
        df_atual_estilizado = df_atual.style.set_properties(**{'text-align': 'center'})
        st.dataframe(df_atual_estilizado, use_container_width=True, hide_index=True)
        
        linhas_opcoes = [f"Linha {i} - Data: {row['Dia']} (Saldo: {row['Saldo']}t)" for i, row in df_atual.iterrows()]
        col_ed, col_btn_ed = st.columns([4, 1])
        with col_ed:
            linha_selecionada = st.selectbox("Selecione um lançamento para editar:", options=linhas_opcoes)
        with col_btn_ed:
            if st.button("Editar Linha", use_container_width=True):
                st.session_state.edit_mode = True
                st.session_state.edit_index = linhas_opcoes.index(linha_selecionada)
                st.rerun()
    else:
        st.info("Nenhum registro lançado para este turno.")

def bloco_cadastro():
    st.markdown("<h2>Cadastrar Novo Operador</h2>", unsafe_allow_html=True)
    with st.form("form_cadastro", clear_on_submit=True):
        nu = st.text_input("Definir Usuário")
        np = st.text_input("Definir Senha", type="password")
        nt = st.selectbox("Turno Fixo", ["1º TURNO", "2º TURNO"])
        
        if st.form_submit_button("Salvar Operador", use_container_width=True):
            if nu and np:
                st.session_state.banco_usuarios[nu] = {"senha": np, "turno_fixo": nt, "role": "operador"}
                st.success(f"Operador '{nu}' cadastrado com sucesso!")
            else:
                st.error("Preencha Usuário e Senha.")

def bloco_login():
    st.markdown('<div class="zion-header">ZION</div>', unsafe_allow_html=True)
    st.markdown('<div class="zion-subtitle">Tecnologia Portuária</div>', unsafe_allow_html=True)
    
    col_esq, col_centro, col_dir = st.columns([1.5, 1.2, 1.5])
    
    with col_centro:
        st.markdown(
            '<div class="login-container">'
            '<h4 style="text-align: center; margin-top: 0px; margin-bottom: 20px; color: #00ff66;">Login de Acesso</h4>', 
            unsafe_allow_html=True
        )
        
        u = st.text_input("Nome de Usuário", placeholder="Digite seu usuário", key="login_user")
        p = st.text_input("Senha", type="password", placeholder="Digite sua senha", key="login_pass")
        
        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        
        if st.button("Entrar no Sistema", use_container_width=True, key="login_submit"):
            banco = st.session_state.banco_usuarios
            if u in banco and banco[u]["senha"] == p:
                st.session_state.logged_in = True
                st.session_state.user_name = u
                st.session_state.role = banco[u]["role"]
                st.session_state.turno_trabalho = "1º TURNO" if banco[u]["role"] == "admin" else banco[u]["turno_fixo"]
                st.session_state.menu_atual = "Lançamentos"
                st.rerun()
            else:
                st.error("Dados inválidos.")
                
        st.markdown('</div>', unsafe_allow_html=True)

def main():
    if st.session_state.logged_in:
        st.sidebar.title("Zion Operações")
        st.sidebar.markdown(f"**Usuário:** {st.session_state.user_name} ({st.session_state.role.upper()})")
        
        if st.session_state.role == "admin":
            st.session_state.turno_trabalho = st.sidebar.selectbox("Visualizar Turno", ["1º TURNO", "2º TURNO"], index=0 if st.session_state.turno_trabalho == "1º TURNO" else 1)
            
        st.sidebar.markdown("---")
        
        if st.sidebar.button("Lançamentos do Turno", use_container_width=True):
            st.session_state.menu_atual = "Lançamentos"
            st.rerun()
        if st.session_state.role == "admin":
            if st.sidebar.button("Global (Consolidado)", use_container_width=True):
                st.session_state.menu_atual = "Global"
                st.rerun()
            if st.sidebar.button("Cadastrar Operador", use_container_width=True):
                st.session_state.menu_atual = "Cadastro"
                st.rerun()
                
        if st.sidebar.button("Sair", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
            
        if st.session_state.menu_atual == "Lançamentos": bloco_painel_poroes(st.session_state.turno_trabalho)
        elif st.session_state.menu_atual == "Global": bloco_consolidado_geral()
        elif st.session_state.menu_atual == "Cadastro": bloco_cadastro()
    else:
        bloco_login()

if __name__ == "__main__":
    main()
