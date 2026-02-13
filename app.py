import streamlit as st
import os
import mne
from nilearn import plotting

st.title("Painel análise de BIDS - PDPD 🧠")
st.write("Bem-vindo ao analisador interativo. Por favor, dê os comandos abaixo:")

caminho_bids = "dados_bids"

# 1. O programa "lê" o que tem no banco de dados e lista para o usuário
try:
    # Acha todas as pastas que começam com "sub-"
    sujeitos_disponiveis = [f for f in os.listdir(caminho_bids) if f.startswith("sub-")]
    sujeitos_disponiveis.sort() # Deixa em ordem alfabética
except FileNotFoundError:
    st.error("Pasta 'dados_bids' não encontrada. Verifique os arquivos do projeto.")
    sujeitos_disponiveis = []

# 2. O COMANDO DO USUÁRIO: Escolhendo o sujeito
if sujeitos_disponiveis:
    sujeito_escolhido = st.selectbox("1️⃣ Qual paciente você quer analisar?", sujeitos_disponiveis)
    
    st.write(f"Você selecionou o paciente: **{sujeito_escolhido}**")
    
    # Caminho para dentro da pasta do paciente escolhido
    caminho_sujeito = os.path.join(caminho_bids, sujeito_escolhido)
    
    # 3. O COMANDO DO USUÁRIO: Escolhendo o tipo de dado (Anatomia, Funcional, EEG)
    tipo_dado = st.radio("2️⃣ Que tipo de exame você quer carregar?", ["Ressonância Anatômica (anat)", "Ressonância Funcional (func)", "Eletroencefalograma (eeg)"])
    
    # Botão de Ação
    if st.button("Executar Análise"):
        st.info("Processando o comando...")
        
        # Aqui entra a lógica dependendo do que ele escolheu!
        if "func" in tipo_dado:
            pasta_func = os.path.join(caminho_sujeito, "func")
            # Procura o arquivo .nii.gz dentro da pasta func
            try:
                arquivos_func = [f for f in os.listdir(pasta_func) if f.endswith(".nii.gz")]
                if arquivos_func:
                    arquivo_alvo = os.path.join(pasta_func, arquivos_func[0])
                    st.success(f"Lendo o arquivo: {arquivos_func[0]}")
                    
                    # Exibe o cérebro
                    st.subheader("Visualização 3D")
                    html_view = plotting.view_img(arquivo_alvo, bg_img=False).get_iframe()
                    st.components.v1.html(html_view, height=400)
                else:
                    st.warning("Nenhum arquivo de ressonância encontrado para este paciente.")
            except FileNotFoundError:
                 st.warning("Este paciente não possui a pasta 'func'.")
                 
        elif "eeg" in tipo_dado:
            st.write("Aqui o programa vai ler os arquivos de EEG usando o MNE!")
            # (Podemos adicionar a lógica do MNE aqui depois!)
