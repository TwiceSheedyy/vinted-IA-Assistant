import streamlit as st
from PIL import Image, ImageEnhance
import google.generativeai as genai

st.set_page_config(page_title="Vinted Assistant PRO", page_icon="🛍️", layout="centered")

st.title("🛍️ Vinted Assistant - Versione Definitiva")

# --- Configurazione API ---
api_key = st.sidebar.text_input("Inserisci la tua Gemini API Key", type="password")
if not api_key and "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]

# --- Funzione per trovare il modello corretto ---
def get_best_model(api_key):
    genai.configure(api_key=api_key)
    try:
        # Cerchiamo tra i modelli quello che supporta la generazione di contenuti
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                # Preferiamo 'gemini-1.5-flash' perché è veloce e gratis
                if 'gemini-1.5-flash' in m.name:
                    return m.name
        # Se non lo trova, prova a restituire il primo disponibile
        return 'gemini-1.5-flash' 
    except Exception:
        return 'gemini-1.5-flash'

# --- 1. CARICAMENTO IMMAGINE ---
uploaded_file = st.file_uploader("Carica la foto del capo", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    
    st.subheader("🔧 Migliora la foto")
    col1, col2, col3 = st.columns(3)
    with col1: rotazione = st.slider("Ruota", -180, 180, 0, step=90)
    with col2: luminosita = st.slider("Luminosità", 0.5, 2.0, 1.0, step=0.1)
    with col3: contrasto = st.slider("Contrasto", 0.5, 2.0, 1.0, step=0.1)
        
    if rotazione != 0:
        image = image.rotate(-rotazione, expand=True)
    image = ImageEnhance.Brightness(image).enhance(luminosita)
    image = ImageEnhance.Contrast(image).enhance(contrasto)
    
    st.image(image, caption="Foto pronta", use_column_width=True)
    
    # --- 2. GENERAZIONE ANNUNCIO ---
    if st.button("Genera Annuncio ✨"):
        if not api_key:
            st.error("Inserisci la chiave API!")
        else:
            with st.spinner("L'IA sta analizzando l'immagine..."):
                try:
                    # Troviamo il nome del modello esatto accettato dal tuo account
                    model_name = get_best_model(api_key)
                    model = genai.GenerativeModel(model_name)
                    
                    prompt = (
                        "Analizza questa foto per Vinted. Scrivi in italiano:\n"
                        "1. Un titolo accattivante con emoji.\n"
                        "2. Una descrizione dettagliata (stile, stato, consigli).\n"
                        "3. Un prezzo consigliato per vendere velocemente."
                    )
                    
                    response = model.generate_content([prompt, image])
                    st.success(f"Annuncio generato con successo!")
                    st.markdown(response.text)
                    
                except Exception as e:
                    st.error(f"Errore: {e}")
                    st.info("Consiglio: Assicurati che la tua chiave API sia attiva su Google AI Studio.")
