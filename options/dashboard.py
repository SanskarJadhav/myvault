import streamlit as st
from database import get_user_data, get_all_banks, add_new_bank, get_all_transactions
import pandas as pd
from encryption import encrypt_data, decrypt_data
import base64
import plotly.express as px

def dashboard(username):
    user_data = get_user_data(username)
    encryption_key = base64.b64decode(user_data["encryption_key"])  # Decrypt the key if needed
    if isinstance(encryption_key, str):
        encryption_key = encryption_key.encode('utf-8')

    def load_banks():
        banks = get_all_banks(username)
        decrypted_banks = []
        for bank in banks:
            decrypted_bank_name = decrypt_data(bank["bank_name"], encryption_key, bank["iv_bank_name"]).decode('utf-8')
            decrypted_starting_amount = decrypt_data(bank["starting_amount"], encryption_key, bank["iv_starting_amount"]).decode('utf-8')
            bank["bank_name"] = decrypted_bank_name
            bank["starting_amount"] = float(decrypted_starting_amount)
            decrypted_banks.append(bank)
        transactions = get_all_transactions(username)
        df = pd.DataFrame(columns = ["Bank", "Type", "Amount"])
        for transaction in transactions:
            decrypted_bank = decrypt_data(transaction["bank"], encryption_key, transaction["iv_bank"]).decode('utf-8')
            decrypted_type = decrypt_data(transaction["type"], encryption_key, transaction["iv_type"]).decode('utf-8')
            decrypted_amount = decrypt_data(transaction["amount"], encryption_key, transaction["iv_amount"]).decode('utf-8')
            df.loc[len(df)] = [decrypted_bank, decrypted_type, float(decrypted_amount)]
        return banks, df
        
    def add_bank(task_name, deadline):
        """Encrypt and add a new bank to the user's bank list."""
        iv_bank_name, encrypted_bank_name = encrypt_data(task_name.encode('utf-8'), encryption_key)
        iv_starting_amount, encrypted_starting_amount = encrypt_data(str(starting_amount).encode('utf-8'), encryption_key)

        # Create the task object with encrypted data
        add_new_bank(username, encrypted_bank_name, iv_bank_name, encrypted_starting_amount, iv_starting_amount)

    banks, transactions = load_banks()
    bank_data = pd.DataFrame(columns=["Bank", "Balance", "No of Transactions", "Credit","Debit"])
    for bank in banks:
        bank_transactions = transactions[transactions["Bank"] == bank["bank_name"]]
        credit = 0
        debit = 0
        if len(bank_transactions) > 0:
            credit = sum(bank_transactions[bank_transactions["Type"] == "Credit"]["Amount"])
            debit =  sum(bank_transactions[bank_transactions["Type"] == "Debit"]["Amount"])
        bank_data.loc[len(bank_data)] = [bank["bank_name"], f"{float(bank["starting_amount"] + credit - debit):.2f}", len(bank_transactions), credit, debit]

    st.table(bank_data[["Bank","Balance","No of Transactions"]])
    exp = st.expander("Add New Bank")
    with exp:
        with st.form("bank_form"):
            bank_name = st.text_input("Bank")
            starting_amount = st.number_input("Starting Amount")
            submit_bank = st.form_submit_button("Add Bank")

            if submit_bank and bank_name and starting_amount:
                add_bank(bank_name, starting_amount)
                st.success(f"Bank '{bank_name}' added!")
                st.rerun()
    fig = px.pie(bank_data, values = "Balance", names="Bank", title="Distribution of Money Across Banks")
    st.plotly_chart(fig)
    fig = px.bar(bank_data, x = "Bank", y=["Credit","Debit"], barmode="group", title = "Credit and Debit for Each Bank")
    st.plotly_chart(fig)
