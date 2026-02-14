import streamlit as st
import os
import tempfile
import mne
import pandas as pd
from nilearn import plotting, image

# Configuração da página para um visual mais limpo
st.set_page_config(page_title="NeuroLab UFABC", page_icon="🧠", layout="wide")

st.title("🧠 NeuroLab: Plataforma de Visualização e Pré-processamento")
st.caption("Projeto PDPD (UFABC)")

# --- BARRA LATERAL (UPLOAD E CONFIGURAÇÕES) ---
with st.sidebar:
    st.header("📂 Entrada de Dados")
    arquivo_carregado = st.file_uploader("Selecione o arquivo (EEG, MRI ou TSV):", 
                                         type=["edf", "set", "vhdr", "nii", "nii.gz", "tsv", "csv"])
    
    st.divider()
    st.info("Esta plataforma suporta o padrão BIDS para organização de dados neurocientíficos.")

# --- LÓGICA DE PROCESSAMENTO ---
if arquivo_carregado:
    nome_arquivo = arquivo_carregado.name
    ext = os.path.splitext(nome_arquivo)[1].lower()
    if nome_arquivo.endswith(".nii.gz"): ext = ".nii.gz"

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(arquivo_carregado.getvalue())
        path = tmp.name

    st.markdown(f"### 📄 Arquivo: `{nome_arquivo}`")
    
    # Criando abas para organizar a visualização e as ferramentas
    aba_vis, aba_proc = st.tabs(["👁️ Visualização", "⚙️ Ferramentas de Processamento"])

    # --- ABA 1: VISUALIZAÇÃO ---
    with aba_vis:
        try:
            if ext in ['.nii', '.nii.gz']:
                vol_mri = image.index_img(path, 0)
                st.subheader("Visualizador de Ressonância Magnética (MRI)")
                view = plotting.view_img(vol_mri, bg_img=False).get_iframe()
                st.components.v1.html(view, height=550)
            
            elif ext in ['.edf', '.set', '.vhdr']:
                st.subheader("Sinais de Eletroencefalograma (EEG)")
                try:
                    dados = mne.io.read_raw(path, preload=True, verbose=False)
                    fig = dados.plot(n_channels=10, duration=5, show=False, scalings='auto')
                except:
                    dados = mne.io.read_epochs_eeglab(path, verbose=False)
                    fig = dados.plot(n_epochs=1, show=False, scalings='auto')
                st.pyplot(fig)
                
            elif ext in ['.tsv', '.csv']:
                st.subheader("Tabela de Eventos/Dados")
                sep = '\t' if ext == '.tsv' else ','
                df = pd.read_csv(path, sep=sep)
                st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Erro na renderização do arquivo: {e}")

    # --- ABA 2: FERRAMENTAS ---
    with aba_proc:
        st.subheader("Análise e Manipulação Técnica")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Gerar Relatório de Metadados"):
                if ext in ['.edf', '.set', '.vhdr']:
                    st.code(f"""
Canais: {len(dados.ch_names)}
Freq. Amostragem: {dados.info['sfreq']} Hz
Bad Channels: {dados.info['bads']}
                    """)
                elif ext in ['.nii', '.nii.gz']:
                    st.code(f"Dimensões do Volume: {vol_mri.shape}")
        
        with col2:
            if st.button("🧹 Simular Filtro Passa-Banda (1-40Hz)"):
                if ext in ['.edf', '.set', '.vhdr']:
                    st.success("Algoritmo de filtragem Butterworth preparado para execução.")
                    st.info("Nota: A aplicação definitiva será integrada na fase de pré-processamento em lote.")

        st.divider()
        st.subheader("📦 Exportação BIDS")
        if st.button("Organizar em Estrutura BIDS"):
            st.warning("Função de reestruturação de pastas (`sub-XX/ses-XX/`) em desenvolvimento.")
            st.download_button("Baixar Template de Estrutura", data="Template BIDS", file_name="template_bids.zip")

else:
    st.info("Aguardando upload de dados para iniciar o laboratório.")
