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
                    # O "Pulo do Gato": Tenta ler contínuo. Se falhar por estar picotado, lê como épocas!
                    try:
                        raw = mne.io.read_raw(caminho_temporario, preload=True)
                        tipo_dado = "continuo"
                    except Exception as erro_interno:
                        if "trials" in str(erro_interno).lower() or "epochs" in str(erro_interno).lower():
                            raw = mne.io.read_epochs_eeglab(caminho_temporario)
                            tipo_dado = "epocas"
                            st.info("ℹ️ Nota do Sistema: Este EEG já está recortado em épocas (trials).")
                        else:
                            raise erro_interno
                    
                    if comando == "1. Informações Básicas":
                        st.write(f"**Quantidade de Canais:** {len(raw.ch_names)}")
                        st.write(f"**Frequência de Amostragem:** {raw.info['sfreq']} Hz")
                        
                        if tipo_dado == "continuo":
                            st.write(f"**Duração Total:** {raw.times[-1]:.2f} segundos")
                        else:
                            st.write(f"**Quantidade de Recortes (Trials):** {len(raw)}")
                            
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
