from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import base64
import streamlit as st
from bson.objectid import ObjectId

connection_string = st.secrets["DATABASE_CONNECTION_STRING"]

client = MongoClient(connection_string)
db = client['user_database']
users_collection = db['users']
tasks_collection = db["tasks"]
transactions_collection = db["transactions"]
banks_collection = db["banks"]
# Create unique index for username
users_collection.create_index([('username', 1)], unique=True)

def register_user(username, encrypted_face, iv_face, encrypted_voice, iv_voice, encryption_key):
    try:
        user_data = {
            "username": username,
            "encrypted_face": encrypted_face,
            "iv_face": iv_face,
            "encrypted_voice": encrypted_voice,
            "iv_voice": iv_voice,
            "encryption_key": base64.b64encode(encryption_key).decode('utf-8')  # Store the key securely
        }
        users_collection.insert_one(user_data)
        return True, "Registration successful"
    except DuplicateKeyError:
        return False, "Username already exists. Please choose a different username."

def get_user_data(username):
    return users_collection.find_one({"username": username})

def get_all_tasks(username):
    """Fetch and decrypt tasks from the database for the logged-in user."""
    tasks = list(tasks_collection.find({"username": username}))
    return tasks

def add_new_task(username, encrypted_task_name, iv_task_name, encrypted_deadline, iv_deadline):
    # Create the task object with encrypted data
    task_data = {
        "username": username,
        "task_name": encrypted_task_name,  # Encrypted task name
        "iv_task_name": iv_task_name,      # Store IV for task name encryption
        "deadline": encrypted_deadline,    # Encrypted deadline
        "iv_deadline": iv_deadline,        # Store IV for deadline encryption
        "completed": False
    }
    tasks_collection.insert_one(task_data)

def update_task_status(task_id, completed):
    """Update task completion status in the database."""
    tasks_collection.update_one({"_id": ObjectId(task_id)}, {"$set": {"completed": completed}})

def delete_task(task_id):
    """Delete a task from the database."""
    tasks_collection.delete_one({"_id": ObjectId(task_id)})

def get_all_banks(username):
    banks = list(banks_collection.find({"username":username}))
    return banks

def add_new_bank(username, encrypted_bank_name, iv_bank_name, encrypted_starting_amount, iv_starting_amount):
    bank_data = {
        "username": username,
        "bank_name": encrypted_bank_name,
        "iv_bank_name": iv_bank_name,
        "starting_amount": encrypted_starting_amount,
        "iv_starting_amount": iv_starting_amount
    }
    banks_collection.insert_one(bank_data)

def get_all_transactions(username):
    """Fetch and decrypt transactions from the database for the logged-in user."""
    transactions = list(transactions_collection.find({"username": username}))
    return transactions

def add_new_transaction(username, encrypted_date, iv_date, encrypted_person, iv_person, encrypted_bank, iv_bank, encrypted_type, iv_type, encrypted_amount, iv_amount, encrypted_remarks, iv_remarks):
    # Create the transaction object with encrypted data
    transaction_data = {
        "username": username,
        "date": encrypted_date,
        "iv_date": iv_date,
        "person": encrypted_person,
        "iv_person": iv_person,
        "bank": encrypted_bank,
        "iv_bank": iv_bank,
        "type": encrypted_type,
        "iv_type": iv_type,
        "amount": encrypted_amount,
        "iv_amount": iv_amount,
        "remarks": encrypted_remarks,
        "iv_remarks": iv_remarks,
    }
    
    transactions_collection.insert_one(transaction_data)

def delete_transaction(transaction_id):
    """Delete a transaction from the database."""
    transactions_collection.delete_one({"_id": ObjectId(transaction_id)})
