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
    model = genai.GenerativeModel('gemini-1.5-flash') # Versão rápida e inteligente
except Exception as e:
    st.error("Erro na Chave API: Verifique se configurou o 'Secrets' no Streamlit.")

st.set_page_config(page_title="NeuroLab Gemini", page_icon="🧠", layout="wide")

st.title("🧠 NeuroLab + Gemini AI 1.5")
st.caption("Assistente de Neuroengenharia conectado ao cérebro do Google.")

# Memória do Chat
if "mensagens" not in st.session_state:
    st.session_state.mensagens = [{"role": "assistant", "content": "Olá, Sabrina! O Gemini está online. Faça o upload do arquivo para começarmos a análise real."}]

# ============================================
# BARRA LATERAL
# ============================================
with st.sidebar:
    st.header("📂 Entrada")
    arquivo_carregado = st.file_uploader("Upload BIDS:", type=["edf", "set", "vhdr", "nii", "nii.gz", "tsv", "csv"])

# ============================================
# LAYOUT E PROCESSAMENTO
# ============================================
col_visual, col_chat = st.columns([1.2, 1])
dados_objeto = None
contexto_tecnico = "Nenhum dado carregado."

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
                contexto_tecnico = f"Arquivo MRI NIfTI. Dimensões: {dados_objeto.shape}. "
            
            elif ext in ['.edf', '.set', '.vhdr']:
                try:
                    dados_objeto = mne.io.read_raw(path, preload=True, verbose=False)
                except:
                    dados_objeto = mne.io.read_epochs_eeglab(path, verbose=False)
                
                st.pyplot(dados_objeto.plot(n_channels=10, show=False, scalings='auto'))
                contexto_tecnico = f"EEG com {len(dados_objeto.ch_names)} canais: {dados_objeto.ch_names}. Freq: {dados_objeto.info['sfreq']}Hz."
        except Exception as e:
            st.error(f"Erro: {e}")

# ============================================
# CHAT REAL COM GEMINI
# ============================================
with col_chat:
    st.subheader("Assistente Gemini ✨")
    
    chat_box = st.container(height=450)
    for m in st.session_state.mensagens:
        chat_box.chat_message(m["role"]).markdown(m["content"])

    if prompt := st.chat_input("Pergunte qualquer coisa sobre o arquivo..."):
        st.session_state.mensagens.append({"role": "user", "content": prompt})
        chat_box.chat_message("user").markdown(prompt)

        with chat_box.chat_message("assistant"):
            with st.spinner("Gemini pensando..."):
                # CRIANDO O PROMPT "ESPECIALIZADO" PARA O GEMINI
                instrucao_ia = f"""
                Você é uma IA especialista em Neuroengenharia e pesquisadora da UFABC. 
                Contexto do arquivo atual: {contexto_tecnico}.
                Pergunta da Sabrina: {prompt}
                Responda de forma técnica, porém objetiva, citando conceitos científicos se necessário.
                """
                
                try:
                    response = model.generate_content(instrucao_ia)
                    texto_resposta = response.text
                except Exception as e:
                    texto_resposta = f"Ops, tive um erro ao falar com o Gemini: {e}"

                st.markdown(texto_resposta)
                st.session_state.mensagens.append({"role": "assistant", "content": texto_resposta})
        st.rerun()
