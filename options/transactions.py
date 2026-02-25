import streamlit as st
import datetime
from database import get_user_data, get_all_banks, get_all_transactions, add_new_transaction, delete_transaction
from encryption import encrypt_data, decrypt_data
import base64

def transactions(username):
    # Fetch user's encryption key from the database
    user_data = get_user_data(username)
    encryption_key = base64.b64decode(user_data["encryption_key"])  # Decrypt the key if needed
    if isinstance(encryption_key, str):
        encryption_key = encryption_key.encode('utf-8')
    #----Helper Functions----
    def load_banks():
        banks = get_all_banks(username)
        decrypted_banks = []
        for bank in banks:
            decrypted_bank = decrypt_data(bank["bank_name"], encryption_key, bank["iv_bank_name"]).decode('utf-8')
            decrypted_banks.append(decrypted_bank)
        return decrypted_banks

    def load_transactions():
        """Fetch and decrypt transactions from the database for the logged-in user."""
        transactions = get_all_transactions(username)
        decrypted_transactions = []
        
        for transaction in transactions:
            # Decrypt transaction name and deadline
            decrypted_date = decrypt_data(transaction["date"], encryption_key, transaction["iv_date"]).decode('utf-8')
            decrypted_person = decrypt_data(transaction["person"], encryption_key, transaction["iv_person"]).decode('utf-8')
            decrypted_bank = decrypt_data(transaction["bank"], encryption_key, transaction["iv_bank"]).decode('utf-8')
            decrypted_type = decrypt_data(transaction["type"], encryption_key, transaction["iv_type"]).decode('utf-8')
            decrypted_amount = decrypt_data(transaction["amount"], encryption_key, transaction["iv_amount"]).decode('utf-8')
            decrypted_remarks = decrypt_data(transaction["remarks"], encryption_key, transaction["iv_remarks"]).decode('utf-8')
            transaction['date'] = decrypted_date
            transaction['person'] = decrypted_person
            transaction['bank'] = decrypted_bank
            transaction['type'] = decrypted_type
            transaction['amount'] = decrypted_amount
            transaction['remarks'] = decrypted_remarks
            decrypted_transactions.append(transaction)
        
        return decrypted_transactions

    def add_transaction(date, person, bank, type, amount, remarks):
        """Encrypt and add a new transaction to the user's transaction list."""
         # Encrypt transaction name and deadline
        iv_date, encrypted_date = encrypt_data(str(date).encode('utf-8'), encryption_key)
        iv_person, encrypted_person = encrypt_data(person.encode('utf-8'), encryption_key)
        iv_bank, encrypted_bank = encrypt_data(bank.encode('utf-8'), encryption_key)
        iv_type, encrypted_type = encrypt_data(type.encode('utf-8'), encryption_key)
        iv_amount, encrypted_amount = encrypt_data(str(amount).encode('utf-8'), encryption_key)
        iv_remarks, encrypted_remarks = encrypt_data(remarks.encode('utf-8'), encryption_key)

        # Create the transaction object with encrypted data
        add_new_transaction(username, encrypted_date, iv_date, encrypted_person, iv_person, encrypted_bank, iv_bank, encrypted_type, iv_type, encrypted_amount, iv_amount, encrypted_remarks, iv_remarks)

    st.write("If the bank is not being displayed, add it in the dashboard")
    # --- transaction input form ---
    with st.form("transaction_form"):
        banks = load_banks()
        date = st.date_input("Date:", max_value=datetime.date.today())
        person = st.text_input("Person:")
        bank = st.selectbox("Bank:", banks)
        type = st.selectbox("Type:", ["Credit", "Debit"])
        amount = st.number_input("Amount:")
        remarks = st.text_input("Remarks:")
        submit_transaction = st.form_submit_button("Add transaction")

        if submit_transaction and date and person and bank and type and amount:
            add_transaction(date, person, bank, type, amount, remarks)
            st.success(f"Transaction added!")
    # --- Load and display transactions ---
    transactions = load_transactions()
    if transactions:
        # --- Checklist for transactions ---
        col1,col2,col3,col4,col5,col6,col7 = st.columns(7)
        with col1:
            st.write("Date:")
        with col2:
            st.write("To/From:")
        with col3:
            st.write("Bank:")
        with col4:
            st.write("Type:")
        with col5:
            st.write("Amount:")
        with col6:
            st.write("Remarks:")
        with col7:
            st.write("Delete Transaction:")
        for transaction in transactions:
            date = transaction["date"]
            person = transaction["person"]
            bank = transaction["bank"]
            type = transaction["type"]
            amount = transaction["amount"]
            remarks = transaction["remarks"]
            transaction_id = transaction["_id"]# Store transaction ID for deletion
            col1,col2,col3,col4,col5,col6,col7 = st.columns(7)
            with col1:
                st.write(date)
            with col2:
                st.write(person)
            with col3:
                st.write(bank)
            with col4:
                st.write(type)
            with col5:
                am = float(amount)
                st.write(f"{am:.2f}")
            with col6:
                st.write(remarks)
            with col7:
                delete_button = st.button("❌", key=transaction_id)
                if delete_button:
                    delete_transaction(transaction_id)
                    st.success("Transaction Deleted")
                    st.rerun()
    else:
        st.info("No transactions added yet.")
