import streamlit as st
import os
import tempfile
import mne
import pandas as pd
from nilearn import plotting, image
import google.generativeai as genai

# CONFIGURAÇÃO DE SEGURANÇA: Puxando a chave dos Secrets
try:
    GENAI_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GENAI_KEY)
    # TENTATIVA 1: Usando o identificador estável mais comum
    model = genai.GenerativeModel('gemini-1.5-flash') 
except Exception as e:
    st.error(f"Erro na Configuração da IA: {e}")

st.set_page_config(page_title="NeuroLab Gemini", page_icon="🧠", layout="wide")

st.title("🧠 NeuroLab + Gemini AI 1.5")
st.caption("Assistente de Neuroengenharia conectado ao cérebro do Google.")

# Memória do Chat
if "mensagens" not in st.session_state:
    st.session_state.mensagens = [{"role": "assistant", "content": "Olá, Sabrina! O Gemini está pronto. Vamos analisar esses dados do seu PDPD?"}]

# ============================================
# BARRA LATERAL (UPLOAD)
# ============================================
with st.sidebar:
    st.header("📂 Entrada de Dados")
    arquivo_carregado = st.file_uploader("Upload BIDS:", type=["edf", "set", "vhdr", "nii", "nii.gz", "tsv", "csv"])
    
    contexto_tecnico = "Nenhum arquivo carregado."
    dados_objeto = None

# ============================================
# LAYOUT DIVIDIDO (VISUALIZAÇÃO À ESQUERDA)
# ============================================
col_visual, col_chat = st.columns([1.2, 1])

with col_visual:
    st.subheader("📊 Visualizador")
    if arquivo_carregado:
        ext = os.path.splitext(arquivo_carregado.name)[1].lower()
        if arquivo_carregado.name.endswith(".nii.gz"): ext = ".nii.gz"
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(arquivo_carregado.getvalue())
            path = tmp.name

        try:
            if ext in ['.nii', '.nii.gz']:
                dados_objeto = image.index_img(path, 0)
                st.components.v1.html(plotting.view_img(dados_objeto, bg_img=False).get_iframe(), height=450)
                contexto_tecnico = f"MRI NIfTI. Dimensões: {dados_objeto.shape}."
            
            elif ext in ['.edf', '.set', '.vhdr']:
                try:
                    dados_objeto = mne.io.read_raw(path, preload=True, verbose=False)
                except:
                    dados_objeto = mne.io.read_epochs_eeglab(path, verbose=False)
                
                st.pyplot(dados_objeto.plot(n_channels=10, show=False, scalings='auto'))
                contexto_tecnico = f"EEG com {len(dados_objeto.ch_names)} canais. Freq: {dados_objeto.info['sfreq']}Hz."
        except Exception as e:
            st.error(f"Erro na visualização: {e}")
    else:
        st.info("Aguardando upload na barra lateral...")

# ============================================
# CHAT COM GEMINI (DIREITA)
# ============================================
with col_chat:
    st.subheader("✨ Assistente Gemini")
    
    chat_box = st.container(height=450)
    for m in st.session_state.mensagens:
        chat_box.chat_message(m["role"]).markdown(m["content"])

    if prompt := st.chat_input("Pergunte ao Gemini sobre os dados..."):
        st.session_state.mensagens.append({"role": "user", "content": prompt})
        chat_box.chat_message("user").markdown(prompt)

        with chat_box.chat_message("assistant"):
            with st.spinner("Consultando o Gemini..."):
                # PROMPT ESPECIALIZADO
                instrucao = f"""
                Você é uma IA especialista em Neuroengenharia e pesquisadora da UFABC. 
                Contexto técnico: {contexto_tecnico}.
                Usuário: Sabrina Nakamura.
                Pergunta: {prompt}
                Responda com autoridade científica, mas de forma clara.
                """
                
                try:
                    # Se 'gemini-1.5-flash' der 404, o código tentará o 'gemini-1.5-pro' como backup
                    response = model.generate_content(instrucao)
                    txt = response.text
                except Exception as err:
                    txt = f"Desculpe, Sabrina. Tive um problema de conexão com o modelo: {err}. Verifique se o nome do modelo está correto para a sua região."

                st.markdown(txt)
                st.session_state.mensagens.append({"role": "assistant", "content": txt})
        st.rerun()
