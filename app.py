import streamlit as st
from transcriptor_ruso import TranscriptorSRH, OpcionesSRH

# 1. Configuración de página
st.set_page_config(
    page_title="Sistema de Romanización Hispánico",
    page_icon="🏛️",
    layout="centered"
)

# 2. CSS para una elegancia inmaculada
st.markdown("""
<style>
    /* Ocultar elementos predeterminados de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Importar tipografías de Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=Inter:wght@300;400;500&display=swap');

    /* Fondo general purísimo */
    .stApp {
        background-color: #FFFFFF;
    }

    /* Títulos principales */
    h1 {
        font-family: 'Playfair Display', serif !important;
        color: #000000 !important;
        text-align: center;
        font-size: 2.8rem !important;
        font-weight: 600 !important;
        letter-spacing: -0.5px;
        padding-top: 2rem;
        padding-bottom: 0px;
    }

    .sub-header {
        font-family: 'Inter', sans-serif;
        text-align: center;
        color: #71717A;
        font-size: 0.85rem;
        letter-spacing: 2.5px;
        text-transform: uppercase;
        margin-bottom: 3.5rem;
        font-weight: 400;
    }

    /* Área de entrada (Cirílico) - Letra más grande y clara */
    .stTextArea textarea {
        font-family: 'Inter', sans-serif !important;
        font-size: 1.25rem !important; /* Tamaño ideal para leer cirílico */
        color: #18181B !important;
        background-color: #FAFAFA !important;
        border: 1px solid #E4E4E7 !important;
        border-radius: 6px !important;
        padding: 1.5rem !important;
        box-shadow: none !important;
        transition: border-color 0.3s ease;
    }
    .stTextArea textarea:focus {
        border-color: #000000 !important;
        box-shadow: 0 0 0 1px #000000 !important;
    }

    /* Botón minimalista */
    .stButton>button {
        font-family: 'Inter', sans-serif !important;
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #D4D4D8 !important;
        border-radius: 4px !important;
        padding: 0.5rem 0rem !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.5px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02) !important;
    }
    .stButton>button:hover {
        border-color: #000000 !important;
        background-color: #FAFAFA !important;
    }

    /* TRUCO MAESTRO: Estilizar el bloque de código para que sea una tarjeta de resultado elegante con botón de copiar nativo */
    [data-testid="stCodeBlock"] pre {
        background-color: #FFFFFF !important;
        border: 1px solid #E4E4E7 !important;
        border-radius: 8px !important;
        padding: 3rem 2rem !important;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.02), 0 8px 10px -6px rgba(0, 0, 0, 0.01) !important;
        text-align: center !important;
    }
    [data-testid="stCodeBlock"] code {
        font-family: 'Playfair Display', serif !important;
        font-size: 2rem !important; /* Tamaño imponente para el resultado */
        color: #09090B !important;
        line-height: 1.5 !important;
        white-space: pre-wrap !important; /* Para que el texto baje de línea si es largo */
    }
    
    /* El botón flotante de copiar dentro del resultado */
    [data-testid="stCodeBlock"] button {
        color: #A1A1AA !important;
    }
    [data-testid="stCodeBlock"] button:hover {
        color: #000000 !important;
    }

    /* Textos de apoyo */
    .etiqueta-input {
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        color: #52525B;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# 3. Lógica del Motor
@st.cache_resource
def load_engine():
    config = OpcionesSRH(colapsar_dobles_consonantes=True)
    return TranscriptorSRH(use_nlp=True, opciones=config)

engine = load_engine()

# --- 4. INTERFAZ VISUAL ---

st.markdown("<h1>Sistema de Romanización Hispánico</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Estándar Filológico Oficial</p>", unsafe_allow_html=True)

st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

st.markdown("<p class='etiqueta-input'>Inserte la grafía original:</p>", unsafe_allow_html=True)
input_text = st.text_area("input", label_visibility="collapsed", placeholder="Ejemplo: Фёдор Достоевский...", height=100)

st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1.5, 1])
with col2:
    submit = st.button("Transcribir", use_container_width=True)

if submit:
    if input_text.strip():
        with st.spinner("Procesando morfología..."):
            res = engine.transcribir(input_text)
        
        st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; font-family:Inter; font-size:0.75rem; color:#A1A1AA; letter-spacing:1px; text-transform:uppercase;'>Transcripción SRH</p>", unsafe_allow_html=True)
        
        # Usamos st.code pero el CSS lo transformará en una tarjeta premium
        st.code(res, language="plaintext")
        
    else:
        st.info("Por favor, ingrese un texto para comenzar.")

st.markdown("<div style='height: 4rem;'></div>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#D4D4D8; font-family:Inter; font-size:0.7rem; letter-spacing:0.5px;'>VERSIÓN 2.0 • ACORDE A LAS NORMAS RAE</p>", unsafe_allow_html=True)
