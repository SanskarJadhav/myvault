import streamlit as st
from database import register_user, get_user_data

def username_register(username):
    user_data = get_user_data(username)
    if user_data:
        st.error("Username already exists. Please choose a different username.")
    else:
        st.session_state.registration_data["username"] = username
        st.session_state.registration_step = 1  # Move to next step: Face image capture
        st.success("Username is available. Please proceed with face capture.")
        st.rerun()

def username_login(username):
    user_data = get_user_data(username)
    if user_data:
        st.session_state.login_data["username"] = username
        st.session_state.login_data["user_data"] = user_data
        st.session_state.login_step = 1  # Move to next step: Face verification
        st.success("Username found. Please proceed with face verification.")
        st.rerun()
    else:
        st.error("Username not found.")
