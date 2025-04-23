

import streamlit as st
import time
from utils import carregar_dados, buscar_resposta

# Configurações da página
st.set_page_config(
    page_title="EducaIA - Assistente Virtual da Universidade",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Aplicar CSS personalizado
def aplicar_css():
    with open("style.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Inicialização do estado da sessão
if 'mensagens' not in st.session_state:
    st.session_state.mensagens = []

if 'base_conhecimento' not in st.session_state:
    st.session_state.base_conhecimento = None
    st.session_state.mensagem_status = None

# Adicionar estado para controlar o indicador de digitação
if 'digitando' not in st.session_state:
    st.session_state.digitando = False

# Adicionar estado para armazenar a pergunta atual
if 'pergunta_atual' not in st.session_state:
    st.session_state.pergunta_atual = None

def adicionar_mensagem(papel, conteudo):
    """Adiciona uma mensagem ao histórico de chat"""
    st.session_state.mensagens.append({"papel": papel, "conteudo": conteudo})

def criar_cabecalho():
    """Cria o cabeçalho personalizado do chat"""
    st.markdown("""
    <div class="chat-header">
        <div class="header-content">
            <div class="header-title">
                <h1 class="header-app-name">EducaIA</h1>
                <p class="header-subtitle">Assistente Virtual da Universidade Católica de Moçambique</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def exibir_mensagens():
    """Exibe o histórico de mensagens"""
    # Cria um contêiner com scroll para as mensagens
    with st.container():
        # Adiciona a classe para permitir scroll
        st.markdown('<div class="mensagens-container">', unsafe_allow_html=True)
        
        # Exibe mensagem inicial quando não há histórico
        if not st.session_state.mensagens:
            st.markdown("""
            <div class="welcome-message">
                <h3>👋 Olá! Sou o EducaIA, seu assistente virtual.</h3>
                <p>Faça uma pergunta sobre a Universidade Católica de Moçambique, polo de Tete.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Exibe todas as mensagens com alinhamento apropriado
            for mensagem in st.session_state.mensagens:
                papel = mensagem["papel"]
                conteudo = mensagem["conteudo"]
                alinhamento = "right" if papel == "user" else "left"
                
                # Apenas mostrar avatar para o assistente, não para o usuário
                if papel == "user":
                    st.markdown(f"""
                    <div class="message-wrapper message-{papel}">
                        <div class="message-bubble message-{papel}-bubble">
                            {conteudo}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="message-wrapper message-{papel}">
                        <div class="message-avatar">🤖</div>
                        <div class="message-bubble message-{papel}-bubble">
                            {conteudo}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Exibe o indicador de digitação apenas se estiver processando
            if st.session_state.digitando:
                st.markdown("""
                <div class="message-wrapper message-assistant">
                    <div class="message-avatar">🤖</div>
                    <div class="typing-indicator">
                        <span></span><span></span><span></span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

def processar_pergunta(pergunta):
    """Processa a pergunta do usuário e adiciona mensagens ao histórico"""
    # Adiciona a pergunta do usuário ao histórico
    adicionar_mensagem("user", pergunta)
    
    # Salva a pergunta no estado da sessão para uso posterior
    st.session_state.pergunta_atual = pergunta
    
    # Ativa o indicador de digitação
    st.session_state.digitando = True
    
    # Força atualização para mostrar o indicador de digitação
    st.rerun()

# Você poderia estar tentando usar a variável pergunta antes de ela ser inicializada
# com o comando st.chat_input()

def main():
    """Função principal do aplicativo"""
    # Aplicar CSS personalizado
    aplicar_css()
    
    # Container centralizado com largura reduzida
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        # Cabeçalho personalizado
        criar_cabecalho()
        
        # Container principal do chat
        with st.container():
            # Carregar a base de conhecimento se não estiver carregada
            if st.session_state.base_conhecimento is None:
                with st.spinner("Carregando base de conhecimento..."):
                    base_conhecimento, mensagem = carregar_dados("dados_faculdade.txt")
                    if len(base_conhecimento) > 0:
                        st.session_state.base_conhecimento = base_conhecimento
                        st.session_state.mensagem_status = mensagem
                        # Adicionar mensagem de boas-vindas apenas na primeira vez
                        if not st.session_state.mensagens:
                            adicionar_mensagem("assistant", "Olá! Sou o EducaIA, assistente virtual da Universidade Católica de Moçambique. Como posso ajudar?")
                    else:
                        st.error(mensagem)
                        st.stop()
            
            # Área de mensagens
            exibir_mensagens()
            
            # Busca a resposta se o indicador de digitação estiver ativo
            if st.session_state.digitando:
                # Pequeno atraso para mostrar a animação
                time.sleep(1)
                
                # Busca a resposta usando a pergunta armazenada no estado
                resultado = buscar_resposta(st.session_state.pergunta_atual, st.session_state.base_conhecimento)
                
                if resultado and resultado.get("resposta"):
                    # Adiciona a resposta ao histórico
                    adicionar_mensagem("assistant", resultado["resposta"])
                else:
                    # Mensagem para quando não encontra resposta
                    mensagem_padrao = ("Desculpe, não encontrei uma resposta para sua pergunta. "
                                      "Por favor, tente reformular ou pergunte sobre outro assunto relacionado à universidade.")
                    adicionar_mensagem("assistant", mensagem_padrao)
                
                # Desativa o indicador de digitação
                st.session_state.digitando = False
                
                # Força atualização para mostrar a resposta
                st.rerun()
            
            # Campo de entrada para novas mensagens
            pergunta_nova = st.chat_input("Ex: Quais cursos são oferecidos na universidade?", key="chat_input")
            
            if pergunta_nova:
                processar_pergunta(pergunta_nova)
        
        # Rodapé
        st.markdown(
            '<div class="chat-footer">© 2025 Universidade Católica de Moçambique - EducaIA v1.0</div>',
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    main()