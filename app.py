import streamlit as st
import pandas as pd
from io import BytesIO

# =====================================================================
# CONFIGURAÇÃO DA PÁGINA (DEVE SER A PRIMEIRA LINHA DO STREAMLIT)
# =====================================================================
st.set_page_config(page_title="Zion Tecnologia", page_icon="🔒", layout="wide")


# =====================================================================
# BLOCO: ESTILIZAÇÃO VISUAL (CSS)
# =====================================================================
def aplicar_estilo_visual():
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            color: #ffffff;
        }
        .custom-box {
            background-color: rgba(30, 41, 59, 0.7);
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.1);
            margin-top: 1rem;
            margin-bottom: 1rem;
        }
        h1, h2, h3 {
            color: #38bdf8 !important;
            text-align: center;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


# =====================================================================
# BLOCO: INICIALIZAÇÃO DO BANCO DE DADOS EM MEMÓRIA
# =====================================================================
def inicializar_banco_usuarios():
    # Estrutura do banco de usuários e turnos
    if 'banco_usuarios' not in st.session_state:
        st.session_state.banco_usuarios = {
            "admin": {"senha": "1234", "turno": "1º TURNO"},
            "alex": {"senha": "zion2026", "turno": "2º TURNO"}
        }
    
    # Estados de controle de login
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_name' not in st.session_state:
        st.session_state.user_name = ""
    if 'turno' not in st.session_state:
        st.session_state.turno = ""

    # MÓDULO 2: Inicializa tabelas separadas para cada turno
    colunas = ["Dia", "Porão 1", "Porão 2", "Porão 3", "Porão 4", "Saldo"]
    if 'tabela_turno_1' not in st.session_state:
        # Exemplo inicial simulado para o 1º turno
        st.session_state.tabela_turno_1 = pd.DataFrame([
            {"Dia": "18/06/2026", "Porão 1": 1500, "Porão 2": 2000, "Porão 3": 0, "Porão 4": 500, "Saldo": 4000}
        ], columns=colunas)
        
    if 'tabela_turno_2' not in st.session_state:
        st.session_state.tabela_turno_2 = pd.DataFrame(columns=colunas)


# =====================================================================
# BLOCO: FUNÇÃO AUXILIAR PARA EXPORTAR EXCEL
# =====================================================================
def converter_para_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Lançamentos')
    dados_processados = output.getvalue()
    return dados_processados


# =====================================================================
# MÓDULO 2: PAINEL DE LANÇAMENTOS POR PORÃO
# =====================================================================
def bloco_painel_poroes(turno_atual):
    st.markdown(f"### 📊 Painel de Controle - {turno_atual}")
    
    # Define qual tabela do banco em memória utilizar baseado no turno logado
    chave_tabela = 'tabela_turno_1' if turno_atual == "1º TURNO" else 'tabela_turno_2'
    df_atual = st.session_state[chave_tabela]

    # --- Sub-Bloco: Formulário para Adicionar Lançamento ---
    with st.expander("➕ Adicionar Novo Lançamento de Porão", expanded=True):
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            data_lancamento = st.date_input("Data", format="DD/MM/YYYY")
        with col2:
            p1 = st.number_input("Porão 1", min_value=0, value=0, step=100)
        with col3:
            p2 = st.number_input("Porão 2", min_value=0, value=0, step=100)
        with col4:
            p3 = st.number_input("Porão 3", min_value=0, value=0, step=100)
        with col5:
            p4 = st.number_input("Porão 4", min_value=0, value=0, step=100)
            
        if st.button("Gravar Dados", use_container_width=True):
            # Calcula o saldo automaticamente somando os porões
            saldo_calculado = p1 + p2 + p3 + p4
            data_formatada = data_lancamento.strftime("%d/%m/%Y")
            
            # Nova linha a ser inserida
            nova_linha = pd.DataFrame([{
                "Dia": data_formatada,
                "Porão 1": p1,
                "Porão 2": p2,
                "Porão 3": p3,
                "Porão 4": p4,
                "Saldo": saldo_calculado
            }])
            
            # Atualiza o DataFrame na sessão
            st.session_state[chave_tabela] = pd.concat([df_atual, nova_linha], ignore_index=True)
            st.success("Lançamento adicionado com sucesso!")
            st.rerun()

    # --- Sub-Bloco: Exibição da Tabela com Linha de Soma ---
    st.markdown("#### Lançamentos Registrados")
    if not df_atual.empty:
        # Cria uma cópia para exibição com a linha de totalização
        df_exibicao = df_atual.copy()
        
        # Garante tipos numéricos para calcular a soma corretamente
        colunas_numericas = ["Porão 1", "Porão 2", "Porão 3", "Porão 4", "Saldo"]
        df_exibicao[colunas_numericas] = df_exibicao[colunas_numericas].apply(pd.to_numeric)
        
        # Cria a linha de SOMA TOTAL
        linha_soma = pd.Series(index=df_exibicao.columns)
        linha_soma["Dia"] = "SOMA TOTAL"
        for col in colunas_numericas:
            linha_soma[col] = df_exibicao[col].sum()
            
        # Adiciona a linha de soma ao final da tabela visual
        df_exibicao = pd.concat([df_exibicao, pd.DataFrame([linha_soma])], ignore_index=True)
        
        # Renderiza a tabela de forma elegante
        st.dataframe(df_exibicao, use_container_width=True, hide_index=True)
        
        # --- Sub-Bloco: Botão de Exportar para Excel ---
        dados_excel = converter_para_excel(df_atual) # Exporta apenas os dados puros (sem a linha visual de soma)
        st.download_button(
            label="📥 Exportar Dados para Excel",
            data=dados_excel,
            file_name=f"Zion_Tecnologia_Porões_{turno_atual.replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    else:
        st.info("Nenhum lançamento registrado para este turno ainda.")


# =====================================================================
# BLOCO: TELA DE CADASTRO DE USUÁRIO
# =====================================================================
def bloco_cadastro_usuario():
    st.markdown('<div class="custom-box">', unsafe_allow_html=True)
    st.subheader("📝 Cadastro de Novo Usuário")
    
    novo_nome = st.text_input("Defina o Nome de Usuário", key="reg_nome")
    nova_senha = st.text_input("Defina a Senha", type="password", key="reg_senha")
    novo_turno = st.selectbox("Vincular ao Turno", ["1º TURNO", "2º TURNO"], key="reg_turno")
    
    if st.button("Salvar Cadastro", use_container_width=True):
        if novo_nome.strip() == "" or nova_senha.strip() == "":
            st.warning("Por favor, preencha todos os campos.")
        elif novo_nome in st.session_state.banco_usuarios:
            st.error("Este usuário já está cadastrado!")
        else:
            st.session_state.banco_usuarios[novo_nome] = {"senha": nova_senha, "turno": novo_turno}
            st.success(f"Usuário '{novo_nome}' cadastrado com sucesso no {novo_turno}!")
            
    st.markdown('</div>', unsafe_allow_html=True)


# =====================================================================
# BLOCO: TELA DE LOGIN
# =====================================================================
def bloco_login():
    st.markdown('<div class="custom-box">', unsafe_allow_html=True)
    st.title("Zion Tecnologia")
    st.subheader("🔒 Área de Acesso")

    nome = st.text_input("Nome de Usuário", key="login_nome")
    senha = st.text_input("Senha", type="password", key="login_senha")
    turno_selecionado = st.selectbox("Qual Turno?", ["1º TURNO", "2º TURNO"], key="login_turno")

    if st.button("Entrar no Sistema", use_container_width=True):
        usuarios = st.session_state.banco_usuarios
        
        if nome in usuarios:
            dados_usuario = usuarios[nome]
            if dados_usuario["senha"] == senha:
                if dados_usuario["turno"] == turno_selecionado:
                    st.session_state.logged_in = True
                    st.session_state.user_name = nome
                    st.session_state.turno = turno_selecionado
                    st.rerun()
                else:
                    st.error(f"Acesso negado! O usuário '{nome}' não está cadastrado no {turno_selecionado}.")
            else:
                st.error("A senha está incorreta.")
        else:
            st.error("Usuário não encontrado.")
            
    st.markdown('</div>', unsafe_allow_html=True)


# =====================================================================
# BLOCO PRINCIPAL (ORQUESTRADOR)
# =====================================================================
def main():
    aplicar_estilo_visual()
    inicializar_banco_usuarios()

    # Fluxo 1: Se o usuário estiver LOGADO, exibe o painel principal do sistema
    if st.session_state.logged_in:
        st.markdown('<div class="custom-box">', unsafe_allow_html=True)
        st.success(f"🎉 Seja Bem Vindo ao Zion Tecnologia, {st.session_state.user_name}!")
        
        # IMPORTANTE: Carrega o Módulo 2 passando o turno do usuário logado
        bloco_painel_poroes(st.session_state.turno)
        
        st.markdown("---")
        if st.button("Sair / Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # Fluxo 2: Se NÃO estiver logado, exibe as abas de Entrada (Login / Cadastro)
    aba_login, aba_cadastro = st.tabs(["Acessar Conta", "Criar Nova Conta"])
    
    with aba_login:
        bloco_login()
        
    with aba_cadastro:
        bloco_cadastro_usuario()


if __name__ == "__main__":
    main()
