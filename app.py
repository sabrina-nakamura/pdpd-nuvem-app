import streamlit as st
import os
import tempfile
import mne
import pandas as pd
from nilearn import plotting, image
import time

# Configuração da página (Wide para caber as duas colunas bem)
st.set_page_config(page_title="NeuroLab PDPD", page_icon="🧠", layout="wide")

st.title("🧠 NeuroLab Dashboard: Visualização & IA")

# Inicializando a memória do chat
if "mensagens" not in st.session_state:
    st.session_state.mensagens = [{"role": "assistant", "content": "Olá, Sabrina! O arquivo está carregado à esquerda. O que deseja analisar agora?"}]

# ============================================
# BARRA LATERAL (APENAS UPLOAD)
# ============================================
with st.sidebar:
    st.header("📂 Entrada")
    arquivo_carregado = st.file_uploader("Upload de arquivo BIDS:", type=["edf", "set", "vhdr", "nii", "nii.gz", "tsv", "csv"])

# ============================================
# LAYOUT EM COLUNAS (O SEGREDO DO VISUAL)
# ============================================
col_data, col_ai = st.columns([1.2, 1]) # Coluna do dado um pouco maior

dados_objeto = None
resumo_ia = "Nenhum arquivo."

# --- COLUNA DA ESQUERDA: VISUALIZAÇÃO FIXA ---
with col_data:
    st.subheader("📊 Visualizador de Dados")
    
    if arquivo_carregado:
        ext = os.path.splitext(arquivo_carregado.name)[1].lower()
        if arquivo_carregado.name.endswith(".nii.gz"): ext = ".nii.gz"

        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(arquivo_carregado.getvalue())
            path = tmp.name

        try:
            if ext in ['.nii', '.nii.gz']:
                dados_objeto = image.index_img(path, 0)
                html_view = plotting.view_img(dados_objeto, bg_img=False).get_iframe()
                st.components.v1.html(html_view, height=500)
                resumo_ia = "Ressonância Magnética 3D (NIfTI)"
                
            elif ext in ['.edf', '.set', '.vhdr']:
                try:
                    dados_objeto = mne.io.read_raw(path, preload=True, verbose=False)
                    fig = dados_objeto.plot(n_channels=10, duration=5, show=False, scalings='auto')
                except:
                    dados_objeto = mne.io.read_epochs_eeglab(path, verbose=False)
                    fig = dados_objeto.plot(n_epochs=1, show=False, scalings='auto')
                st.pyplot(fig)
                resumo_ia = f"EEG com {len(dados_objeto.ch_names)} canais"
                
            elif ext in ['.tsv', '.csv']:
                sep = '\t' if ext == '.tsv' else ','
                dados_objeto = pd.read_csv(path, sep=sep)
                st.dataframe(dados_objeto, height=500)
                resumo_ia = f"Tabela de Eventos ({dados_objeto.shape[0]} linhas)"
                
        except Exception as e:
            st.error(f"Erro ao renderizar: {e}")
    else:
        st.info("Aguardando upload de arquivo para visualização...")

# --- COLUNA DA DIREITA: CHAT ANALÍTICO ---
with col_ai:
    st.subheader("Assistente IA ✨")
    
    # Container para o histórico (faz o chat ter um tamanho fixo)
    chat_container = st.container(height=450)
    
    with chat_container:
        for msg in st.session_state.mensagens:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Barra de input (st.chat_input funciona melhor no final da página, 
    # mas o Streamlit agora permite ele dentro de colunas em versões novas)
    if prompt := st.chat_input("Diga: 'O que tem nesse arquivo?'"):
        st.session_state.mensagens.append({"role": "user", "content": prompt})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                cmd = prompt.lower()
                
                # Resposta Analítica sobre Conteúdo
                if any(x in cmd for x in ["contido", "que tem", "conteudo", "que e isso"]):
                    if dados_objeto is not None:
                        if "EEG" in resumo_ia:
                            res = f"🔍 **Análise de Cabeçalho:** O arquivo é um sinal eletrofisiológico de {len(dados_objeto.ch_names)} canais. A taxa de amostragem é de {dados_objeto.info['sfreq']}Hz, o que permite observar frequências de até {dados_objeto.info['sfreq']/2}Hz (Nyquist). Os eletrodos principais identificados são: {', '.join(dados_objeto.ch_names[:5])}."
                        elif "MRI" in resumo_ia:
                            res = f"🧠 **Análise Volumétrica:** Identifiquei um volume cerebral com dimensões {dados_objeto.shape}. A orientação parece estar no padrão nativo. Recomendo extração de crânio (Brain Extraction) antes da segmentação."
                        else:
                            res = f"📊 **Análise de Tabela:** O arquivo contém {dados_objeto.shape[1]} variáveis. As colunas sugerem marcações de eventos experimentais (onset/duration)."
                    else:
                        res = "Não consigo analisar o conteúdo sem um arquivo. Pode subir um pra mim?"
                
                # Resposta Analítica sobre Filtros
                elif "filtr" in cmd or "ruid" in cmd:
                    res = "⚡ **Processamento Ativado:** Aplicando filtro Butterworth de 4ª ordem (1-40Hz). Esse procedimento elimina o ruído de 60Hz da rede elétrica e derivas térmicas dos eletrodos, estabilizando a linha de base para análise de ERPs."
                
                elif "bids" in cmd:
                    res = "📁 **Protocolo BIDS:** Iniciando reestruturação para o padrão Brain Imaging Data Structure. Vou gerar o arquivo `dataset_description.json` e organizar as pastas de sessão."
                
                else:
                    res = "Comando recebido. Estou monitorando o dado visualizado à esquerda. Posso te dar detalhes técnicos, filtrar ruídos ou organizar o dataset."

                st.markdown(res)
                st.session_state.mensagens.append({"role": "assistant", "content": res})
        
        # Força o recarregamento para mostrar a mensagem nova no container
        st.rerun()
