import streamlit as st
from transcriptor_ruso_v2 import TranscriptorSRH, OpcionesSRH

# 1. Configuración de la página (Elegancia y minimalismo)
st.set_page_config(
    page_title="Norma SRH | Transcriptor Ruso-Español",
    page_icon="🏛️",
    layout="centered"
)

# 2. Estilos CSS personalizados para un aspecto premium
st.markdown("""
<style>
    .titulo-oficial { font-family: 'Georgia', serif; color: #1E3A8A; text-align: center; }
    .subtitulo { text-align: center; color: #4B5563; font-size: 1.1rem; margin-bottom: 2rem; }
    .caja-resultado { 
        background-color: #F3F4F6; 
        padding: 30px; 
        border-radius: 8px; 
        border-left: 5px solid #1E3A8A;
        font-size: 28px; 
        text-align: center; 
        color: #111827; 
        font-weight: 500;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# 3. Encabezado de la Web
st.markdown("<h1 class='titulo-oficial'>Sistema de Romanización Hispánico</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitulo'>Transcriptor Automático Oficial (Norma SRH) • Versión Definitiva</p>", unsafe_allow_html=True)
st.divider()

# 4. Carga del Motor Transcriptor (Caché para mayor velocidad)
@st.cache_resource
def iniciar_motor():
    # Nota: Apagamos el PLN por defecto en la web para que sea instantáneo y no sature el servidor gratuito
    config = OpcionesSRH(colapsar_dobles_consonantes=True)
    return TranscriptorSRH(use_nlp=False, opciones=config)

transcriptor = iniciar_motor()

# 5. Interfaz de Usuario
st.markdown("### Introduzca el texto en ruso:")
texto_entrada = st.text_area("Texto cirílico", height=100, placeholder="Ejemplo: Фёдор Михайлович Достоевский...", label_visibility="collapsed")

if st.button("Transcribir al Español", type="primary", use_container_width=True):
    if texto_entrada.strip():
        with st.spinner("Aplicando rigor filológico..."):
            resultado = transcriptor.transcribir(texto_entrada)
        
        st.markdown("<br><p style='color: #6B7280; font-size: 0.9rem; text-align: center;'>RESULTADO BAJO LA NORMA SRH:</p>", unsafe_allow_html=True)
        st.markdown(f"<div class='caja-resultado'>{resultado}</div>", unsafe_allow_html=True)
    else:
        st.warning("Por favor, introduzca un texto en ruso para comenzar.")

st.divider()
with st.expander("📖 Acerca de la Norma SRH"):
    st.write("El **Sistema de Romanización Hispánico (SRH)** establece un protocolo estricto para transcribir el idioma ruso al español. Equilibra la aproximación fonética, el respeto por la morfología original y la ortografía de la RAE, eliminando influencias anglosajonas o francesas.")
