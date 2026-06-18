import streamlit as st

# =====================================================================
# CONFIGURAÇÃO DA PÁGINA (DEVE SER A PRIMEIRA LINHA DO STREAMLIT)
# =====================================================================
st.set_page_config(page_title="Zion Tecnologia", page_icon="🔒", layout="centered")


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
        h1, h2 {
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
    # Agora a estrutura do banco guarda um dicionário com 'senha' e 'turno' para cada usuário
    if 'banco_usuarios' not in st.session_state:
        st.session_state.banco_usuarios = {
            "admin": {"senha": "1234", "turno": "1º TURNO"},
            "alex": {"senha": "zion2026", "turno": "2º TURNO"}
        }
    
    # Inicializa estados de controle do sistema
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_name' not in st.session_state:
        st.session_state.user_name = ""
    if 'turno' not in st.session_state:
        st.session_state.turno = ""


# =====================================================================
# BLOCO: TELA DE CADASTRO DE USUÁRIO
# =====================================================================
def bloco_cadastro_usuario():
    st.markdown('<div class="custom-box">', unsafe_allow_html=True)
    st.subheader("📝 Cadastro de Novo Usuário")
    
    novo_nome = st.text_input("Defina o Nome de Usuário", key="reg_nome")
    nova_senha = st.text_input("Defina a Senha", type="password", key="reg_senha")
    # Amarrando o turno já no momento do cadastro do usuário
    novo_turno = st.selectbox("Vincular ao Turno", ["1º TURNO", "2º TURNO"], key="reg_turno")
    
    if st.button("Salvar Cadastro", use_container_width=True):
        if novo_nome.strip() == "" or nova_senha.strip() == "":
            st.warning("Por favor, preencha todos os campos.")
        elif novo_nome in st.session_state.banco_usuarios:
            st.error("Este usuário já está cadastrado!")
        else:
            # Salva o usuário amarrando a senha e o turno escolhido
            st.session_state.banco_usuarios[novo_nome] = {
                "senha": nova_senha,
                "turno": novo_turno
            }
            st.success(f"Usuário '{novo_nome}' cadastrado com sucesso no {novo_turno}! Agora você pode fazer login.")
            
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
        
        # 1. Verifica se o usuário existe no sistema
        if nome in usuarios:
            dados_usuario = usuarios[nome]
            
            # 2. Verifica se a senha está correta
            if dados_usuario["senha"] == senha:
                
                # 3. VALIDAÇÃO CRÍTICA: Verifica se o turno selecionado é o mesmo cadastrado
                if dados_usuario["turno"] == turno_selecionado:
                    st.session_state.logged_in = True
                    st.session_state.user_name = nome
                    st.session_state.turno = turno_selecionado
                    st.rerun()
                else:
                    # Se errar o turno, bloqueia o acesso mesmo com a senha certa
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

    # Se estiver logado, mostra o sucesso
    if st.session_state.logged_in:
        st.markdown('<div class="custom-box">', unsafe_allow_html=True)
        st.success(f"🎉 Seja Bem Vindo ao Zion Tecnologia, {st.session_state.user_name}!")
        st.info(f"⏱️ Você entrou usando o: {st.session_state.turno}")
        
        if st.button("Sair / Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # Se NÃO estiver logado, exibe as abas
    aba_login, aba_cadastro = st.tabs(["Acessar Conta", "Criar Nova Conta"])
    
    with aba_login:
        bloco_login()
        
    with aba_cadastro:
        bloco_cadastro_usuario()


if __name__ == "__main__":
    main()
