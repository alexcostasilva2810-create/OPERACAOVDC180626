import streamlit as str

def render_login_page():
    # Configuração de estilo CSS para um visual profissional e plano de fundo
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            color: #ffffff;
        }
        .login-box {
            background-color: rgba(30, 41, 59, 0.7);
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        h1 {
            color: #38bdf8 !important;
            text-align: center;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Inicializa as variáveis de sessão se não existirem
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_name' not in st.session_state:
        st.session_state.user_name = ""
    if 'turno' not in st.session_state:
        st.session_state.turno = ""

    # Se já estiver logado, mostra a mensagem de sucesso
    if st.session_state.logged_in:
        st.success(f"Seja Bem Vindo ao Zion Tecnologia, {st.session_state.user_name}! (Turno: {st.session_state.turno})")
        if st.button("Sair / Logout"):
            st.session_state.logged_in = False
            st.rerun()
        return

    # Estrutura visual da tela de login
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.title("Zion Tecnologia")
    st.subheader("Acesse o Sistema")

    # Usuários simulados para teste (Nome: Senha)
    usuarios_cadastrados = {
        "admin": "1234",
        "usuario1": "senha123"
    }

    # Campos do formulário
    nome = st.text_input("Nome de Usuário")
    senha = st.text_input("Senha", type="password")
    turno = st.selectbox("Selecione o Turno", ["1º TURNO", "2º TURNO"])

    if st.button("Entrar", use_container_width=True):
        if nome in usuarios_cadastrados and usuarios_cadastrados[nome] == senha:
            st.session_state.logged_in = True
            st.session_state.user_name = nome
            st.session_state.turno = turno
            st.rerun()
        else:
            st.error("Senha ou usuário incorreto. Tente novamente.")
            
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    st.set_page_config(page_title="Zion Tecnologia - Login", page_icon="🔒", layout="centered")
    render_login_page()
