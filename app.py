import streamlit as st
from transcriptor_ruso import TranscriptorSRH, OpcionesSRH

# 1. Configuración de página
st.set_page_config(
    page_title="SRH | Sistema de Romanización Hispánico",
    page_icon="📜",
    layout="centered"
)

# 2. CSS de Alta Costura (Modo Oscuro & Elegancia)
st.markdown("""
<style>
    /* Reset y Fondo */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stApp {
        background-color: #050505;
    }

    /* Tipografías Premium */
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;600&family=Inter:wght@200;400&display=swap');

    h1 {
        font-family: 'Cormorant Garamond', serif;
        color: #FFFFFF;
        text-align: center;
        font-size: 3.5rem !important;
        font-weight: 600;
        letter-spacing: -1px;
        margin-bottom: 0px !important;
    }

    .sub-header {
        text-align: center;
        color: #888888;
        font-family: 'Inter', sans-serif;
        font-size: 0.8rem;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-bottom: 50px;
    }

    /* Áreas de Texto */
    .stTextArea textarea {
        background-color: #0A0A0A !important;
        color: #AAAAAA !important;
        border: 1px solid #222222 !important;
        border-radius: 4px !important;
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem !important;
    }

    /* Contenedor de Resultado */
    .resultado-wrapper {
        background-color: #0A0A0A;
        border: 1px solid #1A1A1A;
        border-radius: 0px;
        padding: 60px 20px;
        margin-top: 40px;
        text-align: center;
        transition: all 0.5s ease;
    }

    .label-resultado {
        font-family: 'Inter', sans-serif;
        font-size: 0.7rem;
        color: #444444;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 20px;
    }

    .resultado-texto {
        font-family: 'Cormorant Garamond', serif;
        font-size: 3.8rem;
        color: #E0E0E0;
        font-weight: 600;
        line-height: 1.1;
        margin: 0;
        cursor: pointer;
    }

    /* Botón de Acción */
    .stButton>button {
        background-color: transparent !important;
        color: #FFFFFF !important;
        border: 1px solid #333333 !important;
        border-radius: 0px !important;
        padding: 0.5rem 2rem !important;
        font-family: 'Inter', sans-serif;
        font-weight: 200;
        letter-spacing: 1px;
        transition: all 0.4s ease !important;
        width: 100%;
    }

    .stButton>button:hover {
        border-color: #FFFFFF !important;
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }

    /* Ajustes de Spinner */
    .stSpinner > div {
        border-top-color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. Función para copiar al portapapeles (JavaScript)
def copiar_js(texto):
    js = f"""
        <script>
        navigator.clipboard.writeText("{texto}");
        </script>
    """
    st.components.v1.html(js, height=0)

# 4. Motor SRH
@st.cache_resource
def load_engine():
    config = OpcionesSRH(colapsar_dobles_consonantes=True)
    return TranscriptorSRH(use_nlp=True, opciones=config)

engine = load_engine()

# --- INTERFAZ ---

st.markdown("<h1>Sistema de Romanización Hispánico</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Estándar Filológico • Ruso a Español</p>", unsafe_allow_html=True)

# Input
st.markdown("<p style='color:#444; font-size:0.8rem; margin-bottom:5px;'>TEXTO ORIGINAL (CIRÍLICO)</p>", unsafe_allow_html=True)
input_text = st.text_area("input", label_visibility="collapsed", placeholder="Introduzca texto...", height=100)

col1, col2, col3 = st.columns([1,2,1])
with col2:
    submit = st.button("TRANSCRIBIR")

if submit:
    if input_text.strip():
        with st.spinner(""):
            res = engine.transcribir(input_text)
        
        # Mostrar resultado con diseño inmaculado
        st.markdown(f"""
            <div class='resultado-wrapper'>
                <p class='label-resultado'>Transcripción SRH</p>
                <p class='resultado-texto' id='res_srh'>{res}</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Botón sutil de copiado
        if st.button("COPIAR TEXTO"):
            copiar_js(res)
            st.toast("Copiado al portapapeles", icon="✔")
    else:
        st.info("Entrada vacía.")

st.markdown("<br><br><p style='text-align:center; color:#222; font-size:0.7rem;'>v2.1 • Jurisdicción Filológica SRH</p>", unsafe_allow_html=True)
