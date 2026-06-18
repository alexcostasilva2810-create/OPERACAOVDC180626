import streamlit as st

# Configuração da página (DEVE ser o primeiro comando do Streamlit)
st.set_page_config(page_title="Zion Tecnologia - Login", page_icon="🔒", layout="centered")

def render_login_page():
    # Estilização profissional em CSS para o fundo escuro/azul moderno
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
            margin-top: 2rem;
        }
        h1 {
            color: #38bdf8 !important;
            text-align: center;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Inicializa o estado de login se não existir
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_name' not in st.session_state:
        st.session_state.user_name = ""
    if 'turno' not in st.session_state:
        st.session_state.turno = ""

    # Caso o usuário já tenha logado com sucesso
    if st.session_state.logged_in:
        st.success(f"Seja Bem Vindo ao Zion Tecnologia, {st.session_state.user_name}!")
        st.info(f"Turno ativo: {st.session_state.turno}")
        
        if st.button("Sair / Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
        return

    # Container visual da caixinha de login
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.title("Zion Tecnologia")
    
    # Usuários simulados para teste (Nome: Senha)
    usuarios_cadastrados = {
        "admin": "1234",
        "alex": "zion2026"
    }

    # Campos que o usuário vai preencher
    nome = st.text_input("Nome de Usuário")
    senha = st.text_input("Senha", type="password")
    turno = st.selectbox("Qual Turno?", ["1º TURNO", "2º TURNO"])

    if st.button("Entrar", use_container_width=True):
        if nome in usuarios_cadastrados and usuarios_cadastrados[nome] == senha:
            st.session_state.logged_in = True
            st.session_state.user_name = nome
            st.session_state.turno = turno
            st.rerun()
        else:
            st.error("A senha ou o usuário está incorreto.")
            
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    render_login_page()
