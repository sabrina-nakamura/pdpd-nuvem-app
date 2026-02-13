import streamlit as st
import os
import mne
import matplotlib.pyplot as plt

# Tenta importar a biblioteca de fMRI (se não tiver, não quebra o site)
try:
    from nilearn import plotting
    TEM_NILEARN = True
except ImportError:
    TEM_NILEARN = False

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Sasa Universal Viewer", page_icon="🧠", layout="wide")
st.title("🧠 Sistema Universal de Análise Neurocientífica")
st.markdown("---")

# --- FUNÇÃO INTELIGENTE (O 'CÉREBRO' DO SISTEMA) ---
def analisar_arquivo(caminho_arquivo):
    """Olha para o nome do arquivo e decide qual ferramenta usar."""
    nome = os.path.basename(caminho_arquivo)
    
    if nome.endswith('.vhdr'):
        return "EEG (BrainVision)", "onda", mne.io.read_raw_brainvision
    elif nome.endswith('.edf'):
        return "EEG (EDF)", "onda", mne.io.read_raw_edf
    elif nome.endswith('.set'):
        return "EEG (EEGLAB)", "onda", mne.io.read_raw_eeglab
    elif nome.endswith('.fif'):
        return "MEG (Raw)", "onda", mne.io.read_raw_fif
    elif nome.endswith('.nii') or nome.endswith('.nii.gz'):
        return "Ressonância (NIfTI)", "imagem", None
    else:
        return None, None, None

# --- BARRA LATERAL ---
caminho_bids = "dados_bids"

if os.path.exists(caminho_bids):
    pastas = [f for f in os.listdir(caminho_bids) if f.startswith("sub-")]
    if pastas:
        sujeito_escolhido = st.sidebar.selectbox("Escolha o Participante:", pastas)
    else:
        st.sidebar.warning("Nenhum sujeito (sub-XX) encontrado na pasta.")
        st.stop()
else:
    st.error(f"Pasta '{caminho_bids}' não encontrada! Crie a pasta e coloque os dados lá.")
    st.stop()

# --- VARREDURA INTELIGENTE ---
st.header(f"📂 Varredura do Sujeito: {sujeito_escolhido}")

caminho_sujeito = os.path.join(caminho_bids, sujeito_escolhido)
arquivos_encontrados = []

for root, dirs, files in os.walk(caminho_sujeito):
    for file in files:
        caminho_completo = os.path.join(root, file)
        tipo_descritivo, categoria, funcao_leitura = analisar_arquivo(caminho_completo)
        
        if tipo_descritivo:
            pasta_pai = os.path.basename(root)
            arquivos_encontrados.append({
                "Arquivo": file,
                "Pasta": pasta_pai,
                "Tipo": tipo_descritivo,
                "Categoria": categoria,
                "Caminho": caminho_completo,
                "Funcao": funcao_leitura
            })

if not arquivos_encontrados:
    st.warning("Nenhum arquivo de neuroimagem (EEG ou fMRI) encontrado neste sujeito.")
    st.stop()

# --- VISUALIZAÇÃO DINÂMICA ---
st.subheader("Arquivos Identificados pelo Sistema:")

nomes_abas = [f"{arq['Pasta']}/{arq['Arquivo']}" for arq in arquivos_encontrados]
abas = st.tabs(nomes_abas)

for i, aba in enumerate(abas):
    dado = arquivos_encontrados[i]
    
    with aba:
        st.info(f"🧬 **Tipo Detectado:** {dado['Tipo']}")
        
        if dado['Categoria'] == "onda":
            if st.button(f"Visualizar Sinais ({dado['Arquivo']})", key=f"btn_{i}"):
                with st.spinner("Carregando sinais elétricos..."):
                    try:
                        raw = dado['Funcao'](dado['Caminho'], preload=True, verbose=False)
                        st.pyplot(raw.plot(duration=5, n_channels=10, show=False))
                        st.write("Espectro de Frequência:")
                        st.pyplot(raw.compute_psd().plot(show=False))
                    except Exception as e:
                        st.error(f"Erro ao ler EEG: {e}")

        elif dado['Categoria'] == "imagem":
            if not TEM_NILEARN:
                st.warning("⚠️ Biblioteca 'nilearn' não instalada. Instale no terminal com `pip install nilearn nibabel`.")
            else:
                if st.button(f"Visualizar Cérebro ({dado['Arquivo']})", key=f"btn_{i}"):
                    with st.spinner("Gerando cortes tomográficos..."):
                        try:
                            fig, ax = plt.subplots(figsize=(10, 4))
                            plotting.plot_anat(dado['Caminho'], title=dado['Arquivo'], figure=fig)
                            st.pyplot(fig)
                            st.success("Visualização gerada com sucesso!")
                        except Exception as e:
                            st.error(f"Erro ao plotar fMRI: {e}")

st.markdown("---")
st.caption("Sistema desenvolvido para o PDPD - UFABC")