import streamlit as st
from Crypto.Random import get_random_bytes
from encryption import encrypt_data
from database import register_user
import time


def final_register():
    encryption_key = get_random_bytes(16)  # 16-byte key
    face_image_bytes = st.session_state.registration_data["face_image"]
    voice_data_bytes = st.session_state.registration_data["audio"]

    iv_face, encrypted_face = encrypt_data(face_image_bytes, encryption_key)
    iv_voice, encrypted_voice = encrypt_data(voice_data_bytes, encryption_key)

    # Register user in MongoDB, along with encryption key
    result, message = register_user(
        st.session_state.registration_data["username"],
        encrypted_face, iv_face,
        encrypted_voice, iv_voice,
        encryption_key  # Save the key
    )
    st.write(message)

    if result:
        st.success("Registration successful!")
        st.session_state.logged_in = True
        # Reset registration state
        st.session_state.registration_step = 0
        st.session_state["user_data"] = st.session_state["registration_data"]
        st.session_state.user_data["encryption_key"] = encryption_key
        st.session_state["registration_data"] = {
            "username":"",
            "face_image":None,
            "audio":None
        }
        st.rerun()
    else:
        st.error("Registration failed. Please try again.")
