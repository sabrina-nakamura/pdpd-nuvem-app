import streamlit as st
import os
import tempfile
import mne
import pandas as pd # <-- Biblioteca nova para ler tabelas!
import matplotlib.pyplot as plt
from nilearn import plotting, image

st.title("Laboratório Universal do PDPD 🧠")
st.write("Faça o upload do seu arquivo de neuroimagem, sinais ou tabelas de eventos.")

# 1. A PORTA FOI ABERTA PARA TSV E CSV:
arquivo_carregado = st.file_uploader("Arraste seu arquivo (.edf, .set, .nii, .nii.gz, .tsv, .csv)", 
                                     type=["edf", "set", "vhdr", "nii", "nii.gz", "tsv", "csv"])

if arquivo_carregado is not None:
    nome_arquivo = arquivo_carregado.name
    extensao = os.path.splitext(nome_arquivo)[1].lower()
    if nome_arquivo.endswith(".nii.gz"):
        extensao = ".nii.gz"

    st.divider()
    st.markdown(f"### Arquivo em análise: `{nome_arquivo}`")

    with tempfile.NamedTemporaryFile(delete=False, suffix=extensao) as tmp_file:
        tmp_file.write(arquivo_carregado.getvalue())
        caminho_temporario = tmp_file.name

    # ==========================================
    # ROTA 1: RESSONÂNCIA MAGNÉTICA (NILEARN)
    # ==========================================
    if extensao in ['.nii', '.nii.gz']:
        st.success("👁️ Formato de Imagem Médica (MRI) detectado!")
        comando = st.radio("Escolha a análise:", ["Visualizar Fatias 3D"])
        
        if st.button("Executar Análise"):
            with st.spinner("Fatiando o filme 4D e desenhando o cérebro 3D... Aguarde!"):
                try:
                    imagem_3d = image.index_img(caminho_temporario, 0)
                    st.subheader("Visualização Interativa (Frame 0)")
                    html_view = plotting.view_img(imagem_3d, bg_img=False).get_iframe()
                    st.components.v1.html(html_view, height=450)
                except Exception as e:
                    st.error(f"Erro ao processar a imagem: {e}")

    # ==========================================
    # ROTA 2: ELETROENCEFALOGRAMA (MNE)
    # ==========================================
    elif extensao in ['.edf', '.set', '.vhdr']:
        st.success("🧠 Formato de Ondas Cerebrais (EEG) detectado!")
        comando = st.radio("Escolha a análise:", [
            "1. Informações Básicas", 
            "2. Plotar Ondas Brutas", 
            "3. Aplicar Filtro Passa-Banda (1-30 Hz)"
        ])
        
        if st.button("Executar Análise"):
            with st.spinner("Lendo os sensores do EEG..."):
                try:
                    raw = mne.io.read_raw(caminho_temporario, preload=True)
                    if comando == "1. Informações Básicas":
                        st.write(f"**Quantidade de Canais:** {len(raw.ch_names)}")
                        st.write(f"**Frequência de Amostragem:** {raw.info['sfreq']} Hz")
                        st.write(f"**Duração da Gravação:** {raw.times[-1]:.2f} segundos")
                    elif comando == "2. Plotar Ondas Brutas":
                        fig = raw.plot(n_channels=10, show=False)
                        st.pyplot(fig)
                    elif comando == "3. Aplicar Filtro Passa-Banda (1-30 Hz)":
                        st.info("Filtrando ruídos musculares e de rede elétrica...")
                        raw_filtrado = raw.copy().filter(l_freq=1, h_freq=30)
                        fig = raw_filtrado.plot(n_channels=10, show=False)
                        st.pyplot(fig)
                        st.success("Filtro aplicado com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao processar as ondas: {e}")

    # ==========================================
    # ROTA 3: TABELAS DE EVENTOS (PANDAS)
    # ==========================================
    elif extensao in ['.tsv', '.csv']:
        st.success("📊 Formato de Tabela de Dados detectado!")
        comando = st.radio("Escolha a análise:", ["Visualizar Tabela Bruta", "Resumo Estatístico"])
        
        if st.button("Executar Análise"):
            with st.spinner("Montando a tabela..."):
                try:
                    # TSV significa Tab-Separated Values, então o separador é '\t'
                    separador = '\t' if extensao == '.tsv' else ','
                    
                    # O Pandas lê o arquivo e transforma num DataFrame bonito
                    tabela = pd.read_csv(caminho_temporario, sep=separador)
                    
                    if comando == "Visualizar Tabela Bruta":
                        st.dataframe(tabela) # Desenha a tabela interativa na tela
                    elif comando == "Resumo Estatístico":
                        st.write(tabela.describe())
                except Exception as e:
                    st.error(f"Erro ao ler a tabela: {e}")
