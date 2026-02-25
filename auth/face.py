import streamlit as st
import base64
from encryption import decrypt_data
from deepface import DeepFace

def save_file(uploaded_file, filename): 
    with open(filename, "wb") as f: 
        f.write(uploaded_file)  # Use .getbuffer() only if you have streamlit file uploader
    return filename

def face_login(face_image):
    st.session_state.login_data["face_image"] = face_image.getvalue()

    # Load user data from MongoDB
    user_data = st.session_state.login_data["user_data"]
    encryption_key = base64.b64decode(user_data["encryption_key"])  # Use the stored encryption key

    # Decrypt stored face image
    decrypted_face = decrypt_data(user_data['encrypted_face'], encryption_key, user_data['iv_face'])
            
    # Save face images for DeepFace verification
    img1_path = save_file(decrypted_face, "original_image.jpg")
    img2_path = save_file(face_image.getvalue(), "new_image.jpg")

    # Perform face verification using DeepFace
    try:
        result = DeepFace.verify(
            img1_path=img1_path,
            img2_path=img2_path,
            enforce_detection=False
        )
        face_match = result["verified"]
    except ValueError as e:
        st.error(f"Face verification error: {str(e)}")
        face_match = False

    if face_match:
        st.success("Face match successful. Please proceed with voice verification.")
        st.session_state.login_step = 2  # Move to next step: Voice verification
        st.rerun()
    else:
        st.error("Face match failed. Please try again.")

def face_register(face_image):
    if st.button("Use this Face Image"):
        st.session_state.registration_data["face_image"] = face_image.getvalue()
        st.session_state.registration_step = 2  # Move to next step: Voice input
        st.success("Face image captured. Please proceed with voice recording.")
        st.rerun()
