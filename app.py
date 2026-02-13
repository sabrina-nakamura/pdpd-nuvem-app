import streamlit as st
import os
import tempfile
import mne
import pandas as pd
from nilearn import plotting, image
import time # Importante para simular o tempo de "pensar" da IA

# Configuração da página para parecer mais um aplicativo
st.set_page_config(page_title="NeuroLab PDPD", page_icon="🧠", layout="centered")

st.title("🧠 NeuroLab Universal com IA - PDPD")
st.caption("🚀 Assistente Inteligente para Neuroengenharia. Faça upload e converse com seus dados.")

# ============================================
# INICIALIZANDO A "MEMÓRIA" DO CHAT
# ============================================
# Se ainda não existe um histórico na memória do site, cria uma lista vazia.
if "mensagens" not in st.session_state:
    st.session_state.mensagens = []
    # Adiciona uma mensagem de boas-vindas inicial da IA
    st.session_state.mensagens.append({"role": "assistant", "content": "Olá! Sou sua assistente de neuroengenharia. Faça o upload de um arquivo (EEG, MRI, Eventos) e me diga o que deseja fazer. Posso analisar, sugerir ou até converter dados bagunçados para o padrão BIDS."})

# ============================================
# BARRA LATERAL (UPLOAD FICA AQUI AGORA)
# ============================================
with st.sidebar:
    st.header("📂 Entrada de Dados")
    arquivo_carregado = st.file_uploader("Arraste seu arquivo aqui:", 
                                         type=["edf", "set", "vhdr", "nii", "nii.gz", "tsv", "csv"])
    
    resumo_para_ia = "Nenhum arquivo carregado no momento."
    caminho_temporario = None
    extensao = None

    if arquivo_carregado is not None:
        nome_arquivo = arquivo_carregado.name
        extensao = os.path.splitext(nome_arquivo)[1].lower()
        if nome_arquivo.endswith(".nii.gz"): extensao = ".nii.gz"

        with tempfile.NamedTemporaryFile(delete=False, suffix=extensao) as tmp_file:
            tmp_file.write(arquivo_carregado.getvalue())
            caminho_temporario = tmp_file.name
        
        st.success(f"Arquivo carregado: `{nome_arquivo}`")
        st.divider()
        
        # Mini pré-visualização na barra lateral
        try:
            if extensao in ['.nii', '.nii.gz']:
                st.write("Visualização 3D rápida (Frame 0):")
                imagem_3d = image.index_img(caminho_temporario, 0)
                html_view = plotting.view_img(imagem_3d, bg_img=False, colorbar=False).get_iframe()
                st.components.v1.html(html_view, height=250)
                resumo_para_ia = "Imagem de Ressonância Magnética (fMRI) 3D."
            elif extensao in ['.edf', '.set', '.vhdr']:
                 # Tenta ler contínuo ou épocas
                try:
                    raw = mne.io.read_raw(caminho_temporario, preload=True, verbose=False)
                except:
                    raw = mne.io.read_epochs_eeglab(caminho_temporario, verbose=False)
                st.write(f"EEG: {len(raw.ch_names)} canais, {raw.info['sfreq']}Hz")
                st.pyplot(raw.plot(n_channels=3, show=False, duration=5, scalings='auto'))
                resumo_para_ia = f"Eletroencefalograma (EEG) com {len(raw.ch_names)} canais."
            elif extensao in ['.tsv', '.csv']:
                st.write("Prévia da Tabela:")
                separador = '\t' if extensao == '.tsv' else ','
                tabela = pd.read_csv(caminho_temporario, sep=separador)
                st.dataframe(tabela.head(3))
                resumo_para_ia = f"Tabela de dados com {tabela.shape[0]} linhas."
        except Exception as e:
            st.error(f"Erro na leitura: {e}")
            resumo_para_ia = "Arquivo carregado, mas com erro de leitura."

# ============================================
# ÁREA PRINCIPAL DO CHAT
# ============================================

# 1. Desenha na tela todo o histórico que está na memória
for mensagem in st.session_state.mensagens:
    with st.chat_message(mensagem["role"]):
        st.markdown(mensagem["content"])

# 2. A BARRA DE DIGITAÇÃO (Fica fixa embaixo)
if comando_usuario := st.chat_input("Digite seu comando aqui..."):
    
    # --- TUDO ISSO ACONTECE QUANDO VOCÊ DÁ ENTER ---

    # A. Mostra imediatamente a mensagem do usuário na tela
    with st.chat_message("user"):
        st.markdown(comando_usuario)
    # B. Guarda a mensagem do usuário na memória
    st.session_state.mensagens.append({"role": "user", "content": comando_usuario})

    # C. A IA começa a "pensar"
    with st.chat_message("assistant"):
        with st.spinner("Processando..."):
            time.sleep(1) # Simula um tempo de pensamento da IA
            
            # --- O CÉREBRO DA IA (MOCK) ---
            comando_minusculo = comando_usuario.lower()
            resposta_ia = ""

            # Lógica de Resposta
            if caminho_temporario is None and ("analis" in comando_minusculo or "bids" in comando_minusculo):
                 resposta_ia = "Por favor, faça o upload de um arquivo na barra lateral primeiro para que eu possa analisá-lo."
            
            elif "analis" in comando_minusculo:
                resposta_ia = f"📊 **Análise Técnica:** Baseado no arquivo carregado ({resumo_para_ia}), os dados parecem íntegros. Para este tipo de dado, a próxima etapa recomendada é a verificação de artefatos e a extração de features."
            
            elif "sugest" in comando_minusculo:
                resposta_ia = "💡 **Sugestão de Fluxo:** 1. Pré-processamento (filtros). 2. Segmentação (se for EEG contínuo). 3. Treinamento de modelo supervisionado."
            
            # A ROTINA DE CONVERSÃO BIDS QUE VOCÊ PEDIU!
            elif "bids" in comando_minusculo or "organiz" in comando_minusculo:
                 resposta_ia = """⚙️ **Conversão BIDS Iniciada.**
                 
                 Entendido. Estou reestruturando os dados brutos, criando os arquivos JSON de metadados e organizando as pastas `sub-XX/ses-XX/modality`.
                 
                 *Processando... (Simulação do mne-bids/dcm2niix)*
                 
                 ✅ **Pronto!** O dataset foi padronizado com sucesso. Você pode baixar o pacote completo abaixo:"""
                 
                 # Mostra a resposta de texto da IA
                 st.markdown(resposta_ia)
                 
                 # Mostra o botão de download LOGO ABAIXO da resposta de texto
                 st.download_button(
                     label="📦 Baixar Dataset BIDS Organizado (.zip)",
                     data="Simulação de arquivo ZIP BIDS",
                     file_name="dataset_bids_organizado.zip",
                     mime="application/zip"
                 )
                 # Evita adicionar o texto duas vezes na memória
                 resposta_ia = None 

            else:
                resposta_ia = f"Entendi seu comando: '{comando_usuario}'. Estou olhando para um arquivo do tipo: {resumo_para_ia}. Como posso te ajudar especificamente com isso? Tente pedir uma 'análise', 'sugestão' ou 'conversão BIDS'."

            # Se houve uma resposta de texto simples (não foi a de BIDS com botão), mostra e guarda
            if resposta_ia:
                st.markdown(resposta_ia)
                st.session_state.mensagens.append({"role": "assistant", "content": resposta_ia})
            # Se foi a resposta BIDS, precisamos guardar na memória o que ela disse antes do botão
            elif "bids" in comando_minusculo or "organiz" in comando_minusculo:
                 st.session_state.mensagens.append({"role": "assistant", "content": "⚙️ **Conversão BIDS:** Dados reestruturados e botão de download gerado acima."})
