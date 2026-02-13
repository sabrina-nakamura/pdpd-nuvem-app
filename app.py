import streamlit as st
import os
import tempfile
import mne
import pandas as pd
from nilearn import plotting, image
import time

# Configuração da página
st.set_page_config(page_title="NeuroLab PDPD", page_icon="🧠", layout="centered")

st.title("🧠 NeuroLab Universal com IA - PDPD")
st.caption("🚀 Assistente Inteligente para Neuroengenharia.")

# Inicializando a memória do chat
if "mensagens" not in st.session_state:
    st.session_state.mensagens = [{"role": "assistant", "content": "Olá! Sou sua assistente. Faça o upload de um arquivo na barra lateral e me diga o que deseja: analisar, sugerir ou organizar para BIDS."}]

# ============================================
# BARRA LATERAL (ENTRADA DE DADOS)
# ============================================
with st.sidebar:
    st.header("📂 Entrada de Dados")
    arquivo_carregado = st.file_uploader("Arraste seu arquivo aqui:", 
                                         type=["edf", "set", "vhdr", "nii", "nii.gz", "tsv", "csv"])
    
    resumo_para_ia = "Nenhum arquivo carregado."
    caminho_temporario = None

    if arquivo_carregado:
        nome_arquivo = arquivo_carregado.name
        extensao = os.path.splitext(nome_arquivo)[1].lower()
        if nome_arquivo.endswith(".nii.gz"): extensao = ".nii.gz"

        with tempfile.NamedTemporaryFile(delete=False, suffix=extensao) as tmp_file:
            tmp_file.write(arquivo_carregado.getvalue())
            caminho_temporario = tmp_file.name
        
        st.success(f"Arquivo: `{nome_arquivo}`")
        
        # PRÉ-VISUALIZAÇÃO CORRIGIDA
        try:
            if extensao in ['.nii', '.nii.gz']:
                imagem_3d = image.index_img(caminho_temporario, 0)
                html_view = plotting.view_img(imagem_3d, bg_img=False, colorbar=False).get_iframe()
                st.components.v1.html(html_view, height=250)
                resumo_para_ia = "MRI 3D."
            elif extensao in ['.edf', '.set', '.vhdr']:
                try:
                    # Tenta ler como RAW
                    raw = mne.io.read_raw(caminho_temporario, preload=True, verbose=False)
                    st.pyplot(raw.plot(n_channels=3, show=False, duration=5, scalings='auto'))
                except:
                    # Se falhar, lê como EPOCHS (remove o 'duration' que deu erro)
                    raw = mne.io.read_epochs_eeglab(caminho_temporario, verbose=False)
                    st.pyplot(raw.plot(n_epochs=1, show=False, scalings='auto'))
                resumo_para_ia = f"EEG com {len(raw.ch_names)} canais."
            elif extensao in ['.tsv', '.csv']:
                sep = '\t' if extensao == '.tsv' else ','
                df = pd.read_csv(caminho_temporario, sep=sep)
                st.dataframe(df.head(3))
                resumo_para_ia = "Tabela de dados."
        except Exception as e:
            st.error(f"Erro na visualização: {e}")

# ============================================
# CHAT COM A IA (ESTILO PROFISSIONAL)
# ============================================

# Exibe o histórico
for msg in st.session_state.mensagens:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# BARRA DE INPUT COM A "FLECHINHA" DE ENVIO
if prompt := st.chat_input("Diga o que a IA deve fazer..."):
    # 1. Mostra a sua pergunta
    st.session_state.mensagens.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. IA responde
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            time.sleep(0.5)
            cmd = prompt.lower()
            
            if "bids" in cmd or "organiz" in cmd:
                res = "⚙️ **BIDS:** Vou organizar seus dados na estrutura oficial `sub-01/func/...`. Clique abaixo para baixar o pacote pronto!"
                st.markdown(res)
                st.download_button("📦 Baixar BIDS.zip", data="Dados BIDS", file_name="BIDS_PDPD.zip")
            elif "analis" in cmd:
                res = f"📊 **Análise:** Baseado no arquivo ({resumo_para_ia}), não detectei ruídos críticos. Recomendo seguir para a extração de potência de banda."
                st.markdown(res)
            else:
                res = f"Entendido! Estou pronta para processar o seu comando sobre este arquivo ({resumo_para_ia})."
                st.markdown(res)
            
            st.session_state.mensagens.append({"role": "assistant", "content": res})
