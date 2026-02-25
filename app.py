import streamlit as st
from auth.auth import login, register, logout
from options.dashboard import dashboard
from options.deadlines import deadlines
from options.transactions import transactions

# Initialize session state for login and registration steps
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "registration_step" not in st.session_state:
    st.session_state.registration_step = 0
if "registration_data" not in st.session_state:
    st.session_state.registration_data = {
        "username": "",
        "face_image": None,
        "audio": None
    }
if "login_step" not in st.session_state:
    st.session_state.login_step = 0
if "login_data" not in st.session_state:
    st.session_state.login_data = {
        "username": "",
        "face_image": None,
        "audio": None
    }

# Main function for the app
def main():
    st.set_page_config(page_title="MyVault", layout="wide", initial_sidebar_state="expanded", page_icon = ":coin:")
    if not st.session_state.logged_in:
        option = st.sidebar.selectbox("Choose", ["Register", "Login"])
        if option == "Register":
            register()
            st.write('<script>location.reload()</script>', unsafe_allow_html=True)
        elif option == "Login":
            login()
            st.write('<script>location.reload()</script>', unsafe_allow_html=True)
    else:
        username = st.session_state.user_data["username"]
        st.title(f"Welcome, {username}! 👋")
        button = st.sidebar.button("Logout")

        if button:
            logout()
            st.write('<script>location.reload()</script>', unsafe_allow_html=True)
    
        option = st.sidebar.radio("Pages", ["Dashboard", "Transactions", "Reminders"])

        if option == "Dashboard":
            dashboard(username)
        elif option == "Reminders":
            deadlines(username)
        elif option == "Transactions":
            transactions(username)


if __name__ == '__main__':
    main()
