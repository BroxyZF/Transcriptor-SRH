import streamlit as st
import streamlit.components.v1 as components
from transcriptor_ruso import TranscriptorSRH, OpcionesSRH

# 1. Configuración de página (Inmaculada)
st.set_page_config(
    page_title="Sistema de Romanización Hispánico",
    page_icon="🏛️",
    layout="centered"
)

# 2. CSS Global - Refinamiento Extremo
st.markdown("""
<style>
    /* Limpieza total del lienzo */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Importación de fuentes premium */
    @import url('https://fonts.googleapis.com/css2?family=Lora:wght@400;500;600&family=Inter:wght@300;400;500&display=swap');

    .main {
        background-color: #FFFFFF;
    }

    /* Título principal con autoridad */
    h1 {
        font-family: 'Lora', serif;
        font-weight: 600;
        color: #111827;
        text-align: center;
        font-size: 2.2rem;
        letter-spacing: -0.5px;
        padding-bottom: 0px;
        margin-top: -20px;
    }

    /* Subtítulo técnico */
    .sub-header {
        font-family: 'Inter', sans-serif;
        text-align: center;
        color: #6B7280;
        font-size: 0.80rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 50px;
        font-weight: 400;
    }

    /* Área de texto cirílico (Lectura cómoda y elegante) */
    .stTextArea textarea {
        font-family: 'Lora', serif !important;
        font-size: 1.2rem !important;
        color: #374151 !important;
        background-color: #FAFAFA !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 8px !important;
        padding: 20px !important;
        line-height: 1.6 !important;
        box-shadow: none !important;
        transition: all 0.3s ease;
    }
    .stTextArea textarea:focus {
        background-color: #FFFFFF !important;
        border-color: #9CA3AF !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03) !important;
    }

    /* Etiqueta encima del cuadro de texto */
    .stTextArea label {
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        color: #4B5563 !important;
        font-size: 0.9rem !important;
        margin-bottom: 10px !important;
    }

    /* Botón de acción principal */
    .stButton>button {
        font-family: 'Inter', sans-serif;
        background-color: #111827;
        color: #FFFFFF;
        border-radius: 6px;
        border: none;
        padding: 0.7rem 2rem;
        font-size: 0.95rem;
        font-weight: 500;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-top: 10px;
    }
    .stButton>button:hover {
        background-color: #374151;
        box-shadow: 0 6px 10px -1px rgba(0, 0, 0, 0.15);
    }
</style>
""", unsafe_allow_html=True)

# 3. Motor en Caché
@st.cache_resource
def load_engine():
    config = OpcionesSRH(colapsar_dobles_consonantes=True)
    return TranscriptorSRH(use_nlp=True, opciones=config)

engine = load_engine()

# 4. Función constructora de la Tarjeta de Resultado HTML/JS
def renderizar_resultado(texto):
    html_code = f"""
    <link href="https://fonts.googleapis.com/css2?family=Lora:wght@400;500&family=Inter:wght@400;500&display=swap" rel="stylesheet">
    <style>
        body {{
            margin: 0;
            display: flex;
            justify-content: center;
            background-color: transparent;
        }}
        .caja-resultado {{
            background-color: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 12px;
            padding: 45px 30px;
            text-align: center;
            width: 100%;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.03);
            font-family: 'Inter', sans-serif;
            box-sizing: border-box;
        }}
        .etiqueta {{
            font-size: 0.70rem;
            color: #9CA3AF;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin: 0 0 25px 0;
        }}
        .texto-transcrito {{
            font-family: 'Lora', serif;
            font-size: 2.2rem;
            color: #111827;
            font-weight: 500;
            margin: 0 0 35px 0;
            line-height: 1.4;
        }}
        .btn-copiar {{
            background-color: transparent;
            border: 1px solid #D1D5DB;
            color: #4B5563;
            padding: 10px 24px;
            border-radius: 30px;
            font-size: 0.85rem;
            font-family: 'Inter', sans-serif;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }}
        .btn-copiar:hover {{
            background-color: #F9FAFB;
            color: #111827;
            border-color: #9CA3AF;
        }}
        .btn-copiar.exito {{
            background-color: #F0FDF4;
            color: #166534;
            border-color: #BBF7D0;
        }}
    </style>
    <div class="caja-resultado">
        <p class="etiqueta">Transcripción Oficial</p>
        <p class="texto-transcrito">{texto}</p>
        <button class="btn-copiar" id="copyBtn" onclick="copiarAlPortapapeles()">
            <svg id="copyIcon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
            <span id="copyText">Copiar resultado</span>
        </button>
    </div>
    <script>
        function copiarAlPortapapeles() {{
            navigator.clipboard.writeText(`{texto}`).then(() => {{
                const btn = document.getElementById('copyBtn');
                const text = document.getElementById('copyText');
                
                btn.classList.add('exito');
                text.innerText = '¡Copiado al portapapeles!';
                
                setTimeout(() => {{
                    btn.classList.remove('exito');
                    text.innerText = 'Copiar resultado';
                }}, 2500);
            }});
        }}
    </script>
    """
    components.html(html_code, height=300, scrolling=True)


# 5. Estructura de la Web
st.markdown("<h1>Sistema de Romanización Hispánico</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Estándar Filológico Transcriptor • Ruso a Español</p>", unsafe_allow_html=True)

input_text = st.text_area("Texto fuente (Cirílico):", placeholder="Ej. Александр Сергеевич Пушкин...", height=140)

col1, col2, col3 = st.columns([1,2,1])
with col2:
    submit = st.button("Transcribir al Español", use_container_width=True)

if submit:
    if input_text.strip():
        with st.spinner("Aplicando rigor filológico..."):
            res = engine.transcribir(input_text)
        
        st.markdown("<br>", unsafe_allow_html=True)
        renderizar_resultado(res)
    else:
        st.info("Por favor, ingrese un texto para transcribir.")

st.markdown("<br><p style='text-align:center; color:#cbd5e1; font-size:0.75rem;'>Norma SRH v2.0 • Arbitraje ortográfico de la RAE activo</p>", unsafe_allow_html=True)
