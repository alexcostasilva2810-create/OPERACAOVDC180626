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
    # Se a nossa "base de dados" temporária não existir, cria ela com os padrões
    if 'banco_usuarios' not in st.session_state:
        st.session_state.banco_usuarios = {
            "admin": "1234",
            "alex": "zion2026"
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
    
    novo_nome = st.text_input("Alex Silva", key="246371")
    nova_senha = st.text_input("Defina a Senha", type="password", key="reg_senha")
    
    if st.button("Salvar Cadastro", use_container_width=True):
        if novo_nome.strip() == "" or nova_senha.strip() == "":
            st.warning("Por favor, preencha todos os campos.")
        elif novo_nome in st.session_state.banco_usuarios:
            st.error("Este usuário já está cadastrado!")
        else:
            # Adiciona o novo usuário no nosso dicionário de sessão
            st.session_state.banco_usuarios[novo_nome] = nova_senha
            st.success(f"Usuário '{novo_nome}' cadastrado com sucesso! Agora você pode fazer login.")
            
    st.markdown('</div>', unsafe_allow_html=True)


# =====================================================================
# BLOCO: TELA DE LOGIN
# =====================================================================
def bloco_login():
    st.markdown('<div class="custom-box">', unsafe_allow_html=True)
    st.title("Zion Tecnologia")
    st.subheader("🔒 Área de Acesso")

    # Campos de entrada
    nome = st.text_input("Nome de Usuário", key="login_nome")
    senha = st.text_input("Senha", type="password", key="login_senha")
    turno = st.selectbox("Qual Turno?", ["1º TURNO", "2º TURNO"], key="login_turno")

    if st.button("Entrar no Sistema", use_container_width=True):
        # Busca os usuários atualizados no banco em memória
        usuarios = st.session_state.banco_usuarios
        
        if nome in usuarios and usuarios[nome] == senha:
            st.session_state.logged_in = True
            st.session_state.user_name = nome
            st.session_state.turno = turno
            st.percent(100) # Pequena firula visual
            st.rerun()
        else:
            st.error("A senha ou o usuário está incorreto.")
            
    st.markdown('</div>', unsafe_allow_html=True)


# =====================================================================
# BLOCO PRINCIPAL (ORQUESTRADOR)
# =====================================================================
def main():
    aplicar_estilo_visual()
    inicializar_banco_usuarios()

    # Caso o usuário já tenha logado com sucesso, mostra as boas-vindas
    if st.session_state.logged_in:
        st.markdown('<div class="custom-box">', unsafe_allow_html=True)
        st.success(f"🎉 Seja Bem Vindo ao Zion Tecnologia, {st.session_state.user_name}!")
        st.info(f"⏱️ Turno ativo: {st.session_state.turno}")
        
        if st.button("Sair / Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # Se NÃO estiver logado, exibe as abas na tela de entrada
    aba_login, aba_cadastro = st.tabs(["Acessar Conta", "Criar Nova Conta"])
    
    with aba_login:
        bloco_login()
        
    with aba_cadastro:
        bloco_cadastro_usuario()


if __name__ == "__main__":
    main()
