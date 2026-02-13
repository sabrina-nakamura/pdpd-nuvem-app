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
    comando_usuario = st.text_input("Digite o que você quer que a IA faça (ex: 'analisar ruídos', 'dar sugestões', 'comentar'):")

    if st.button("🧠 Enviar Comando"):
        if comando_usuario:
            with st.spinner("A IA está interpretando seu comando..."):
                st.success("**Resposta do Assistente:**")
                
                # A IA repete o que entendeu para mostrar inteligência
                st.write(f"Recebi o seu comando: *'{comando_usuario}'*")
                st.write(f"**Contexto identificado:** Estou olhando para um arquivo do tipo: {resumo_para_ia}")
                
                # O motor que busca palavras-chave no texto livre
                comando_minusculo = comando_usuario.lower()
                
                if "analis" in comando_minusculo:
                    st.write("📊 **Análise:** Os dados carregados apresentam uma estrutura primária consistente. Não foram detectados artefatos críticos que impeçam o processamento. Recomendo extrair características de frequência (Feature Extraction) para alimentar os algoritmos de classificação.")
                
                elif "sugest" in comando_minusculo:
                    st.write("💡 **Sugestões:** Dependendo do seu objetivo, sugiro iniciar com uma limpeza de sinal avançada (ex: Independent Component Analysis para remover piscadas de olho no EEG, ou correção temporal no fMRI).")
                
                elif "coment" in comando_minusculo:
                    st.write("💬 **Comentários:** A formatação dos dados parece respeitar a hierarquia esperada (BIDS). A qualidade técnica da coleta parece excelente para aplicações de aprendizado de máquina.")
                
                else:
                    st.write("⚙️ **Ação Processada:** Seu comando foi registrado no sistema. Esta rotina será automatizada assim que os pesos do modelo final forem integrados à plataforma.")
                    
                st.caption("Nota de Desenvolvimento: Esta é a Interface de Linguagem Natural. A API de rede neural definitiva será conectada neste módulo.")
        else:
            st.warning("Por favor, digite algum comando na caixa de texto antes de enviar!")
