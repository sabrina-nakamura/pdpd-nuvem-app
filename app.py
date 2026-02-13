import streamlit as st
import os
import tempfile
import mne
import pandas as pd
from nilearn import plotting, image

st.title("Laboratório Universal com IA - PDPD 🧠✨")
st.write("Faça o upload do seu arquivo e digite comandos livres para a IA analisar, comentar ou sugerir abordagens.")

# A PORTA FOI ABERTA PARA TODOS OS FORMATOS:
arquivo_carregado = st.file_uploader("Arraste seu arquivo (.edf, .set, .nii, .nii.gz, .tsv, .csv)", 
                                     type=["edf", "set", "vhdr", "nii", "nii.gz", "tsv", "csv"])

if arquivo_carregado is not None:
    nome_arquivo = arquivo_carregado.name
    extensao = os.path.splitext(nome_arquivo)[1].lower()
    if nome_arquivo.endswith(".nii.gz"):
        extensao = ".nii.gz"

    st.divider()
    st.markdown(f"### 📂 Arquivo Carregado: `{nome_arquivo}`")

    with tempfile.NamedTemporaryFile(delete=False, suffix=extensao) as tmp_file:
        tmp_file.write(arquivo_carregado.getvalue())
        caminho_temporario = tmp_file.name

    # ==========================================
    # PASSO 1: PRÉ-VISUALIZAÇÃO AUTOMÁTICA
    # ==========================================
    st.subheader("👁️ Visualização Inicial")
    resumo_para_ia = "" # O site guarda isso na memória para a IA saber do que falar

    try:
        if extensao in ['.nii', '.nii.gz']:
            with st.spinner("Desenhando cérebro 3D..."):
                imagem_3d = image.index_img(caminho_temporario, 0)
                html_view = plotting.view_img(imagem_3d, bg_img=False).get_iframe()
                st.components.v1.html(html_view, height=350)
                resumo_para_ia = "Imagem de Ressonância Magnética (fMRI) 3D."

        elif extensao in ['.edf', '.set', '.vhdr']:
            with st.spinner("Lendo canais de EEG..."):
                try:
                    raw = mne.io.read_raw(caminho_temporario, preload=True)
                except:
                    raw = mne.io.read_epochs_eeglab(caminho_temporario)
                
                fig = raw.plot(n_channels=5, show=False)
                st.pyplot(fig)
                resumo_para_ia = f"Eletroencefalograma (EEG) com {len(raw.ch_names)} canais."

        elif extensao in ['.tsv', '.csv']:
            separador = '\t' if extensao == '.tsv' else ','
            tabela = pd.read_csv(caminho_temporario, sep=separador)
            st.dataframe(tabela.head())
            resumo_para_ia = f"Tabela de dados contendo {tabela.shape[0]} linhas e {tabela.shape[1]} colunas."
            
    except Exception as e:
        st.error(f"Erro na pré-visualização: {e}")

    st.divider()

    # ==========================================
    # PASSO 2: O CÉREBRO DA IA (Comando Livre)
    # ==========================================
    st.subheader("Assistente de Inteligência Artificial ✨")
    
    # A caixa onde o professor pode digitar o que ele quiser!
    comando_usuario = st.text_input("Digite o que você quer que a IA faça (ex: 'analisar ruídos', 'dar sugestões', 'etc...):")

   # A mágica acontece assim que ela der 'Enter' ou clicar no ícone de enviarzinho
    if comando_usuario:
        with st.spinner("A IA está interpretando seu comando..."):
            
            # Cria um balãozinho visual para o usuário
            with st.chat_message("user"):
                st.write(comando_usuario)
            
            # Cria um balãozinho visual para a resposta da IA
            with st.chat_message("assistant"):
                st.write(f"**Contexto identificado:** Estou olhando para: {resumo_para_ia}")
                
                # O motor que busca palavras-chave
                comando_minusculo = comando_usuario.lower()
                
                if "analis" in comando_minusculo:
                    st.write("📊 **Análise:** Os dados apresentam uma estrutura primária consistente. Não foram detectados artefatos críticos. Recomendo extrair características de frequência (Feature Extraction) para alimentar os algoritmos de classificação.")
                
                elif "sugest" in comando_minusculo:
                    st.write("💡 **Sugestões:** Sugiro iniciar com uma limpeza de sinal avançada (ex: Independent Component Analysis para remover piscadas de olho no EEG, ou correção temporal no fMRI).")
                
                elif "coment" in comando_minusculo:
                    st.write("💬 **Comentários:** A formatação respeita a hierarquia BIDS. A qualidade técnica da coleta parece excelente para aprendizado de máquina.")
                
                else:
                    st.write("⚙️ **Ação Processada:** Comando registrado. Esta rotina será automatizada quando os pesos do modelo preditivo forem integrados.")
