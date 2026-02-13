import streamlit as st
import os
import tempfile
import mne
import matplotlib.pyplot as plt
from nilearn import plotting, image

st.title("Laboratório Universal do PDPD 🧠")
st.write("Faça o upload do seu arquivo de neuroimagem ou sinais. O sistema fará o roteamento automático.")

# A CAIXA ABERTA
arquivo_carregado = st.file_uploader("Arraste seu arquivo (.edf, .set, .nii, .nii.gz)", type=["edf", "set", "vhdr", "nii", "nii.gz"])

if arquivo_carregado is not None:
    nome_arquivo = arquivo_carregado.name
    
    # Descobrindo a extensão real do arquivo
    extensao = os.path.splitext(nome_arquivo)[1].lower()
    if nome_arquivo.endswith(".nii.gz"):
        extensao = ".nii.gz"

    st.divider()
    st.markdown(f"### Arquivo em análise: `{nome_arquivo}`")

    # TRUQUE DE MESTRE: Criando o arquivo físico temporário para as bibliotecas lerem
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
                    # O SEGREDO: Pega o primeiro "frame" (tempo 0) do filme 4D do fMRI
                    imagem_3d = image.index_img(caminho_temporario, 0)
                    
                    # Desenha a visualização usando apenas esse frame 3D
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
                    # O MNE lê o arquivo temporário
                    raw = mne.io.read_raw(caminho_temporario, preload=True)
                    
                    if comando == "1. Informações Básicas":
                        st.write(f"**Quantidade de Canais:** {len(raw.ch_names)}")
                        st.write(f"**Frequência de Amostragem:** {raw.info['sfreq']} Hz")
                        st.write(f"**Duração da Gravação:** {raw.times[-1]:.2f} segundos")
                        
                    elif comando == "2. Plotar Ondas Brutas":
                        # MNE desenha o gráfico e o Streamlit exibe
                        fig = raw.plot(n_channels=10, show=False)
                        st.pyplot(fig)
                        
                    elif comando == "3. Aplicar Filtro Passa-Banda (1-30 Hz)":
                        st.info("Filtrando ruídos musculares e de rede elétrica...")
                        # Copia o dado original e aplica o filtro
                        raw_filtrado = raw.copy().filter(l_freq=1, h_freq=30)
                        fig = raw_filtrado.plot(n_channels=10, show=False)
                        st.pyplot(fig)
                        st.success("Filtro aplicado com sucesso!")
                        
                except Exception as e:
                    st.error(f"Erro ao processar as ondas: {e}")
