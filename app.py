import streamlit as st
from transcriptor_ruso import TranscriptorSRH, OpcionesSRH

# Configuración de página (Sin anchors en los headers)
st.set_page_config(
    page_title="Sistema de Romanización Hispánico",
    page_icon="📜",
    layout="centered"
)

# CSS para máxima elegancia y ocultar elementos sobrantes
st.markdown("""
<style>
    /* Ocultar el menú de Streamlit y el pie de página para limpieza total */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Tipografía y Colores */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@400;500&display=swap');

    .main {
        background-color: #ffffff;
        font-family: 'Inter', sans-serif;
    }

    h1 {
        font-family: 'Playfair Display', serif;
        color: #1a1a1a;
        text-align: center;
        padding-bottom: 0px;
    }

    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1rem;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 40px;
    }

    .resultado-container {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 40px;
        margin-top: 30px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }

    .resultado-texto {
        font-size: 32px;
        color: #0f172a;
        font-weight: 500;
        margin: 0;
    }

    /* Estilo del botón */
    .stButton>button {
        background-color: #1a1a1a;
        color: white;
        border-radius: 6px;
        border: none;
        padding: 0.6rem 2rem;
        font-weight: 500;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #444;
        border: none;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Lógica del Motor
@st.cache_resource
def load_engine():
    # Ahora intentará usar el PLN si lo pusiste en requirements.txt
    config = OpcionesSRH(colapsar_dobles_consonantes=True)
    return TranscriptorSRH(use_nlp=True, opciones=config)

engine = load_engine()

# --- INTERFAZ ---

# Títulos usando Markdown directo para evitar el símbolo de cadena
st.markdown("<h1>Sistema de Romanización Hispánico</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Estándar Filológico Transcriptor • Ruso a Español</p>", unsafe_allow_html=True)

# Entrada de texto
st.markdown("<p style='font-weight:500; color:#444;'>Texto en cirílico:</p>", unsafe_allow_html=True)
input_text = st.text_area("input", label_visibility="collapsed", placeholder="Escriba aquí (ej. Александр Пушкин)...", height=120)

col1, col2, col3 = st.columns([1,2,1])
with col2:
    submit = st.button("Procesar Transcripción", use_container_width=True)

if submit:
    if input_text.strip():
        with st.spinner("Procesando..."):
            res = engine.transcribir(input_text)
        
        st.markdown(f"""
            <div class='resultado-container'>
                <p style='font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; margin-bottom: 10px;'>Resultado SRH</p>
                <p class='resultado-texto'>{res}</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Por favor, ingrese un texto para transcribir.")

st.markdown("<br><br><p style='text-align:center; color:#cbd5e1; font-size:0.8rem;'>Norma SRH v2.0 • Basado en los acuerdos de la RAE</p>", unsafe_allow_html=True)
