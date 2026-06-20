import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURAÇÃO DA PÁGINA (ORIGINAL)
st.set_page_config(page_title="Zion Operações", layout="wide")

# 2. CONEXÃO COM O GOOGLE SHEETS
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Erro na ligação com o Google Sheets: {e}")
    conn = None

# Meta de referência original do seu painel
REFERENCIA_CONTRATUAL = 50000.0

def carregar_dados_nuvem():
    """Busca os dados em tempo real no Google Sheets."""
    if conn:
        try:
            # ttl=0 força o Streamlit a buscar dados novos direto da nuvem sem usar cache antigo
            df = conn.read(ttl=0)
            if df.empty:
                return pd.DataFrame(columns=["Turno", "Dia", "Porção 1", "Porção 2", "Porção 3", "Porção 4", "Porção 5", "Saldo", "Usuário", "Hora do Registro"])
            
            # Garante que os campos de porções sejam numéricos para não quebrar os cálculos de soma
            colunas_numéricas = ["Porção 1", "Porção 2", "Porção 3", "Porção 4", "Porção 5", "Saldo"]
            for col in colunas_numéricas:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
            return df
        except Exception:
            return pd.DataFrame(columns=["Turno", "Dia", "Porção 1", "Porção 2", "Porção 3", "Porção 4", "Porção 5", "Saldo", "Usuário", "Hora do Registro"])
    return pd.DataFrame()

def atualizar_planilha_nuvem(df_novo):
    """Grava o DataFrame atualizado de volta na nuvem usando as credenciais configuradas."""
    if conn:
        try:
            # Envia os dados atualizados para a planilha Google
            conn.update(data=df_novo)
            return True
        except Exception as e:
            st.error(f"Erro ao gravar os dados na nuvem: {e}")
            return False
    return False

# Inicialização segura dos dados na sessão para evitar erros de tela vermelha (IndexError)
if "dados_operacao" not in st.session_state:
    st.session_state.dados_operacao = carregar_dados_nuvem()

# Atualiza a variável local de dados
df_atual = st.session_state.dados_operacao

# -----------------------------------------------------------------------------
# MENU LATERAL (LAYOUT ORIGINAL DO SEU VÍDEO)
# -----------------------------------------------------------------------------
st.sidebar.title("Zion Operações")
st.sidebar.write("🟢 **Usuário:** admin (ADMIN)")

if "menu_atual" not in st.session_state:
    st.session_state.menu_atual = "Lançamentos"

if st.sidebar.button("Lançamentos do Turno", use_container_width=True):
    st.session_state.menu_atual = "Lançamentos"
if st.sidebar.button("Global (Consolidado)", use_container_width=True):
    st.session_state.menu_atual = "Global"
if st.sidebar.button("Cadastrar Operador", use_container_width=True):
    st.session_state.menu_atual = "Cadastrar Operador"
st.sidebar.button("Sair", use_container_width=True)

st.sidebar.markdown("---")
# Menu de seleção de turno conforme o seu vídeo original
st.session_state.turno_trabalho = st.sidebar.selectbox("Visualizar Turno", ["1º TURNO", "2º TURNO"])

# -----------------------------------------------------------------------------
# TELA 1: LANÇAMENTOS DO TURNO (RESTALRADA EXATAMENTE IGUAL AO SEU VÍDEO)
# -----------------------------------------------------------------------------
if st.session_state.menu_atual == "Lançamentos":
    st.header(f"Lançamentos Atuais - {st.session_state.turno_trabalho}")
    
    with st.expander("🔹 Novo Lançamento (5 Porções)", expanded=True):
        col_data, col_p1, col_p2, col_p3, col_p4, col_p5 = st.columns(6)
        
        with col_data:
            data_lanc = st.date_input("Data", value=datetime.now())
        with col_p1:
            p1 = st.number_input("Porção 1 (t)", min_value=0.0, step=50.0, value=0.0)
        with col_p2:
            p2 = st.number_input("Porção 2 (t)", min_value=0.0, step=50.0, value=0.0)
        with col_p3:
            p3 = st.number_input("Porção 3 (t)", min_value=0.0, step=50.0, value=0.0)
        with col_p4:
            p4 = st.number_input("Porção 4 (t)", min_value=0.0, step=50.0, value=0.0)
        with col_p5:
            p5 = st.number_input("Porção 5 (t)", min_value=0.0, step=50.0, value=0.0)
            
        btn_gravar = st.button("Gravar Lançamento", type="primary", use_container_width=True)
        
    if btn_gravar:
        saldo_lancamento = p1 + p2 + p3 + p4 + p5
        
        # Cria o novo registro mapeado exatamente com os nomes das colunas da sua planilha Google
        novo_registro = {
            "Turno": st.session_state.turno_trabalho,
            "Dia": data_lanc.strftime("%d/%m/%Y"),
            "Porção 1": p1,
            "Porção 2": p2,
            "Porção 3": p3,
            "Porção 4": p4,
            "Porção 5": p5,
            "Saldo": saldo_lancamento,
            "Usuário": "admin",
            "Hora do Registro": datetime.now().strftime("%H:%M:%S")
        }
        
        # Puxa os dados frescos diretamente do Google Sheets para evitar sobreposição
        df_fresco = carregar_dados_nuvem()
        df_atualizado = pd.concat([df_fresco, pd.DataFrame([novo_registro])], ignore_index=True)
        
        # Atualiza a planilha e reinicia o estado
        if atualizar_planilha_nuvem(df_atualizado):
            st.session_state.dados_operacao = df_atualizado
            st.success("Lançamento gravado com sucesso no Google Sheets! 🚀")
            st.rerun()

    st.subheader("Histórico do Turno")
    # Exibe apenas os registros pertencentes ao turno selecionado (Filtro Original)
    if not df_atual.empty and "Turno" in df_atual.columns:
        df_turno = df_atual[df_atual["Turno"] == st.session_state.turno_trabalho]
        if not df_turno.empty:
            st.dataframe(df_turno, use_container_width=True, hide_index=True)
        else:
            st.info(f"Nenhum registro lançado ainda para o {st.session_state.turno_trabalho}.")
    else:
        st.info(f"Nenhum registro lançado ainda para o {st.session_state.turno_trabalho}.")

    # --- SEÇÃO DE EDIÇÃO ORIGINAL DO SEU VÍDEO (RESTALRADA COM PROTEÇÃO ANTI-ERRO) ---
    st.markdown("---")
    if not df_atual.empty and "Turno" in df_atual.columns:
        df_turno_edit = df_atual[df_atual["Turno"] == st.session_state.turno_trabalho]
        if not df_turno_edit.empty:
            opcoes_edicao = []
            indices_reais = []
            
            # Mapeia as opções mantendo a formatação e guardando o índice original do DataFrame
            for idx, row in df_turno_edit.iterrows():
                opcoes_edicao.append(f"Linha {idx} - Data: {row['Dia']} (Saldo: {row['Saldo']})")
                indices_reais.append(idx)
                
            selecionado = st.selectbox("Selecione um lançamento para editar:", opcoes_edicao)
            
            # Validação anti IndexError: impede a leitura de linhas caso a lista mude repentinamente
            if selecionado:
                posicao_lista = opcoes_edicao.index(selecionado)
                st.session_state.edit_index = indices_reais[posicao_lista]
                
                if st.session_state.edit_index < len(df_atual):
                    try:
                        row_edit = df_atual.iloc[st.session_state.edit_index]
                        st.button("Editar Linha", use_container_width=True)
                    except IndexError:
                        pass
        else:
            st.info("Nenhum dado lançado nos turnos até o momento.")
    else:
        st.info("Nenhum dado lançado nos turnos até o momento.")

# -----------------------------------------------------------------------------
# TELA 2: PAINEL GERENCIAL GLOBAL (CONSOLIDADO ORIGINAL DO SEU VÍDEO)
# -----------------------------------------------------------------------------
elif st.session_state.menu_atual == "Global":
    st.header("Painel Gerencial Global (5 Porções)")
    
    # Executa a matemática unificada acumulando os dados inseridos em todos os turnos
    if not df_atual.empty:
        total_p1 = df_atual["Porção 1"].sum() if "Porção 1" in df_atual.columns else 0.0
        total_p2 = df_atual["Porção 2"].sum() if "Porção 2" in df_atual.columns else 0.0
        total_p3 = df_atual["Porção 3"].sum() if "Porção 3" in df_atual.columns else 0.0
        total_p4 = df_atual["Porção 4"].sum() if "Porção 4" in df_atual.columns else 0.0
        total_p5 = df_atual["Porção 5"].sum() if "Porção 5" in df_atual.columns else 0.0
        total_lancado = df_atual["Saldo"].sum() if "Saldo" in df_atual.columns else 0.0
    else:
        total_p1 = total_p2 = total_p3 = total_p4 = total_p5 = total_lancado = 0.0
        
    quanto_falta = REFERENCIA_CONTRATUAL - total_lancado
    if quanto_falta < 0:
        quanto_falta = 0.0

    # Layout de blocos de métricas original
    col_m1, col_m2, col_m3, col_m4, col_m5, col_mt = st.columns(6)
    col_m1.metric("Total Porção 1", f"{total_p1:,.0f} t".replace(",", "."))
    col_m2.metric("Total Porção 2", f"{total_p2:,.0f} t".replace(",", "."))
    col_m3.metric("Total Porção 3", f"{total_p3:,.0f} t".replace(",", "."))
    col_m4.metric("Total Porção 4", f"{total_p4:,.0f} t".replace(",", "."))
    col_m5.metric("Total Porção 5", f"{total_p5:,.0f} t".replace(",", "."))
    col_mt.metric("TOTAL JÁ LANÇADO", f"{total_lancado:,.0f} t".replace(",", "."))
    
    col_ref, col_falta = st.columns(2)
    with col_ref:
        st.info(f"**REFERÊNCIA CONTRATUAL:**\n### {REFERENCIA_CONTRATUAL:,.0f} t".replace(",", "."))
    with col_falta:
        st.warning(f"**QUANTO FALTA ATINGIR:**\n### {quanto_falta:,.0f} t".replace(",", "."))
        
    st.markdown("---")
    st.subheader("Histórico de Lançamentos Realizados")
    
    # Exibição da tabela unificada com todos os lançamentos feitos
    if not df_atual.empty:
        st.dataframe(df_atual, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum dado lançado nos turnos até o momento.")
        
    # Botão original de exportar para PDF mantido exatamente no rodapé da página
    st.button("Exporter Relatório Global em PDF", type="secondary", use_container_width=True)

# -----------------------------------------------------------------------------
# TELA 3: CADASTRO DE OPERADORES (TELA DE BACKUP)
# -----------------------------------------------------------------------------
elif st.session_state.menu_atual == "Cadastrar Operador":
    st.header("Controle de Acesso - Cadastrar Operador")
    st.info("Área de gerenciamento administrativa.")
