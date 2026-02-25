import streamlit as st
from encryption import decrypt_data
import base64
import time
import speech_recognition as sr
import numpy as np
from pydub import AudioSegment
from io import BytesIO
import wave
import os
from speechbrain.pretrained import SpeakerRecognition
import tempfile
import shutil
import soundfile as sf

# speaker_model = SpeakerRecognition.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb", savedir="tmp")
@st.cache_resource
def load_speaker_model():
    return SpeakerRecognition.from_hparams(
        source="speechbrain/spkrec-ecapa-voxceleb"
    )

speaker_model = load_speaker_model()

decrypted_voice_sample_rate = 90000

def transcribe_audio(audio_file):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(BytesIO(audio_file)) as source:
            audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_sphinx(audio_data)
            return text
        except sr.UnknownValueError:
            return "Sorry, could not understand the audio."
        except sr.RequestError as e:
            return f"Error with speech recognition service; {e}"
    except Exception as e:
        return f"Error processing audio file: {e}"

def voice_register(audio):
    st.session_state.registration_data["audio"] = audio
    st.session_state.registration_step = 3  # Ready to register
    st.success("Voice recording captured. Ready to register.")

def voice_login(audio):
    st.session_state.login_data["audio"] = audio
    user_data = st.session_state.login_data["user_data"]
    encryption_key = base64.b64decode(user_data['encryption_key'])
    decrypted_voice = decrypt_data(user_data['encrypted_voice'], encryption_key, user_data['iv_voice'])

    with open("decrypted_audio.wav", "wb") as f:
        sf.write(f, np.frombuffer(decrypted_voice, dtype=np.int16), decrypted_voice_sample_rate)
        
    # Save the recorded audio to another .wav file
    with open("audio2.wav", "wb") as f:
        f.write(audio)

    score, prediction = speaker_model.verify_files("decrypted_audio.wav", "audio2.wav")
    st.write(prediction)

    transcription = transcribe_audio(audio)
    st.write(transcription)
    sentence = st.session_state.random_sentence

    if transcription.lower() == sentence.lower() and prediction:
        st.session_state.logged_in = True
        st.success("Login successful!")
        st.session_state.login_step = 0
        st.session_state["user_data"] = st.session_state["login_data"]
        st.session_state.user_data["encryption_key"] = encryption_key
        st.session_state["login_data"] = {
            "username":"",
            "face_image":None,
            "audio":None
        }
        st.rerun()
    else:
        st.error("Voice match failed. Please try again.")

