import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
from gtts import gTTS
from googletrans import Translator

# --- CONFIGURACIÓN DE LA APP ---
st.set_page_config(page_title="Traductor con Flow 🔥", page_icon="🎤", layout="centered")

# --- TÍTULO ---
st.title("🎤 Traductor con Flow - Real Hasta La Muerte 💀")
st.subheader("Habla tu mensaje y conviértelo en audio con estilo Anuel")

# --- PORTADA ---
try:
    image = Image.open("anuel_portada.png")  # Asegúrate de tener esta imagen en tu carpeta
    st.image(image, width=300)
except FileNotFoundError:
    st.warning("No se encontró la imagen de Anuel. ¡Pero el flow sigue intacto!")

# --- SIDEBAR ---
with st.sidebar:
    st.subheader("🎧 ¿Cómo funciona?")
    st.write("Presiona el botón, habla tu mensaje, tradúcelo al idioma que quieras y escucha cómo suena con flow 🔥")

# --- BOTÓN DE ESCUCHA ---
st.write("🎙️ Toca el botón y habla tu mensaje con actitud:")

stt_button = Button(label="🎤 Escuchar con Flow", width=300, height=50)
stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
"""))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="anuel_listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

# --- PROCESAMIENTO ---
if result and "GET_TEXT" in result:
    st.success("🔥 ¡Texto capturado con flow!")
    st.write(f"🗣️ Lo que dijiste: *{result.get('GET_TEXT')}*")

    os.makedirs("temp", exist_ok=True)
    translator = Translator()
    text = str(result.get("GET_TEXT"))

    st.markdown("## 🌍 Configura tu traducción:")

    in_lang = st.selectbox("Idioma de entrada", ("Español", "Inglés", "Coreano", "Japonés", "Mandarín"))
    out_lang = st.selectbox("Idioma de salida", ("Español", "Inglés", "Coreano", "Japonés", "Mandarín"))

    lang_map = {
        "Español": "es",
        "Inglés": "en",
        "Coreano": "ko",
        "Japonés": "ja",
        "Mandarín": "zh-cn"
    }

    input_language = lang_map[in_lang]
    output_language = lang_map[out_lang]

    accent = st.selectbox("🎙️ Elige el acento del audio", (
        "Defecto", "México", "Estados Unidos", "Reino Unido", "Australia", "Canadá"
    ))

    tld_map = {
        "Defecto": "com",
        "México": "com.mx",
        "Estados Unidos": "com",
        "Reino Unido": "co.uk",
        "Australia": "com.au",
        "Canadá": "ca"
    }

    tld = tld_map[accent]

    def text_to_speech(input_language, output_language, text, tld):
        translation = translator.translate(text, src=input_language, dest=output_language)
        trans_text = translation.text
        tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
        file_name = text[:20].replace(" ", "_") or "audio"
        tts.save(f"temp/{file_name}.mp3")
        return file_name, trans_text

    show_text = st.checkbox("Mostrar texto traducido")

    if st.button("🎧 Convertir a Audio con Flow"):
        file_name, translated_text = text_to_speech(input_language, output_language, text, tld)
        audio_path = f"temp/{file_name}.mp3"
        with open(audio_path, "rb") as audio_file:
            st.audio(audio_file.read(), format="audio/mp3", start_time=0)
        st.success("🎶 ¡Tu audio está listo, bro!")

        if show_text:
            st.markdown("## 📝 Texto traducido:")
            st.write(translated_text)

    # --- LIMPIEZA ---
    def remove_old_files(days):
        now = time.time()
        limit = now - (days * 86400)
        for f in glob.glob("temp/*.mp3"):
            if os.path.getmtime(f) < limit:
                os.remove(f)

    remove_old_files(7)

# --- FOOTER ---
st.markdown("---")
st.caption("💿 App creada con el flow de Anuel AA | Traductor con estilo | Real Hasta La Muerte 💀")
