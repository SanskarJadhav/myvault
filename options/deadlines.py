import streamlit as st
import datetime
from database import get_user_data, get_all_tasks, add_new_task, delete_task, update_task_status
from encryption import encrypt_data, decrypt_data
import base64

def deadlines(username):
    # Fetch user's encryption key from the database
    user_data = get_user_data(username)
    encryption_key = base64.b64decode(user_data["encryption_key"])  # Decrypt the key if needed
    if isinstance(encryption_key, str):
        encryption_key = encryption_key.encode('utf-8')

    #----Helper Functions----

    def load_tasks():
        """Fetch and decrypt tasks from the database for the logged-in user."""
        tasks = get_all_tasks(username)
        decrypted_tasks = []
        
        for task in tasks:
            # Decrypt task name and deadline
            decrypted_task_name = decrypt_data(task['task_name'], encryption_key, task['iv_task_name']).decode('utf-8')
            decrypted_deadline = decrypt_data(task['deadline'], encryption_key, task['iv_deadline']).decode('utf-8')
            task['task_name'] = decrypted_task_name
            task['deadline'] = decrypted_deadline
            decrypted_tasks.append(task)
        
        return decrypted_tasks

    def add_task(task_name, deadline):
        """Encrypt and add a new task to the user's task list."""
         # Encrypt task name and deadline
        iv_task_name, encrypted_task_name = encrypt_data(task_name.encode('utf-8'), encryption_key)
        iv_deadline, encrypted_deadline = encrypt_data(str(deadline).encode('utf-8'), encryption_key)

        # Create the task object with encrypted data
        add_new_task(username, encrypted_task_name, iv_task_name, encrypted_deadline, iv_deadline)

    # --- Task input form ---
    with st.form("task_form"):
        task_name = st.text_input("Payment")
        deadline = st.date_input("Due Date", min_value=datetime.date.today())
        submit_task = st.form_submit_button("Add Reminder")

        if submit_task and task_name:
            add_task(task_name, deadline)
            st.success(f"Reminder for '{task_name}' added!")

    # --- Load and display tasks ---
    tasks = load_tasks()
    if tasks:
        completed_tasks = sum(1 for task in tasks if task["completed"])
        total_tasks = len(tasks)
        
        # --- Progress bar ---
        progress = completed_tasks / total_tasks
        st.progress(progress, "Progress Bar of Payments Made")
        
        if completed_tasks == total_tasks:
            st.success("You've made all your payments!")

        # --- Checklist for tasks ---
        for task in tasks:
            task_name = task["task_name"]
            task_deadline = task["deadline"]  # This will already be decrypted
            task_completed = task["completed"]
            task_id = task["_id"]  # Store task ID for deletion

            # Display task with checkbox and delete button
            col1, col2 = st.columns([8, 2])  # Adjust column widths as needed
            with col1:
                checked = st.checkbox(f"{task_name} (Deadline: {task_deadline})", value=task_completed)
                if checked != task_completed:
                    # Update task completion status in the database
                    update_task_status(task_id, checked)
                    st.rerun()  # Refresh the app to show updated tasks
            with col2:
                if st.button("❌", key=task_id):  # Use an emoji or text for delete
                    delete_task(task_id)
                    st.success(f"Reminder for '{task_name}' deleted!")
                    st.rerun()  # Refresh the app to show updated tasks
    else:
        st.info("No reminders have been added yet.")
