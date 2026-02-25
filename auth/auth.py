import streamlit as st
from audio_recorder_streamlit import audio_recorder
from auth.username import username_login, username_register
from auth.face import face_login, face_register
from auth.voice import voice_login, voice_register
from auth.final_register import final_register
import time
import random
import warnings
warnings.filterwarnings("ignore")


# Verbal recognition, can add more sentences to this list to increase randomness
def generate_random_sentence():
    sentencelist = ["This ends in one way", "Welcome to the Matrix", "How are you feeling",
                    "This is actually better", "We learn from our mistakes", "The world is changing"]
    sentence = random.choice(sentencelist)
    return sentence

# Registration process
def register():
    st.session_state.login_step = 0
    st.title("Register")

    # Step 1: Ask for username and check availability
    if st.session_state.registration_step == 0:
        username = st.text_input("Enter Username")
        if username and st.button("Check Username"):
            username_register(username)

    # Step 2: Capture face image
    if st.session_state.registration_step == 1:
        face_image = st.camera_input(label="Capture Face Image for Registration")
        
        if face_image:
            face_register(face_image)
        
    # Step 3: Capture voice input
    if st.session_state.registration_step == 2:
        audio = audio_recorder(sample_rate=41_000)

        if audio:
            st.audio(audio, format="audio/wav")
            if st.button("Use this Voice Recording"):
                voice_register(audio)
    
    # Step 4: Register the user
    if st.session_state.registration_step == 3 and st.button("Register"):
        final_register()


# Login process
def login():
    st.session_state.registration_step = 0
    st.title("Login")

    # Step 1: Ask for username and check if it exists
    if st.session_state.login_step == 0:
        username = st.text_input("Enter Username")
        
        if username and st.button("Check Username"):
            username_login(username)
            

    # Step 2: Face verification
    if st.session_state.login_step == 1:
        face_image = st.camera_input(label="Capture Face Image for Authentication")
    
        if face_image:
            if st.button("Verify Face"):
                face_login(face_image)


    # Step 3: Voice verification
    if st.session_state.login_step == 2:
        sentence = generate_random_sentence()
        if 'random_sentence' not in st.session_state:
            st.session_state.random_sentence = sentence
        
        st.write("Please state the following words:")
        st.write(st.session_state.random_sentence)
        
        audio = audio_recorder()

        if audio:
            st.audio(audio, format="audio/wav")
            if st.button("Verify Voice"):
                voice_login(audio)

def logout():
    st.session_state.logged_in = False
    st.session_state.registration_step = 0
    st.session_state.login_step = 0
    st.session_state.user_data = {
        "username":"",
        "face_image": None,
        "audio": None,
        "encryption_key": None
    }
    st.success("You have been logged out.")
    st.rerun()
