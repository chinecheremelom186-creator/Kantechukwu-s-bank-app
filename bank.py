import streamlit as st
import json
import os
import random
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Apex Virtual Bank", page_icon="🏦", layout="centered")

# --- DATABASE MANAGEMENT ---
DB_FILE = "bank_db.json"

def load_db():
    # Load database from file, or create empty dictionary if it doesn't exist
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}

def save_db(data):
    # Save database changes permanently to the file
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Initialize session state for DB and login
if 'db' not in st.session_state:
    st.session_state.db = load_db()
if 'logged_in_acc' not in st.session_state:
    st.session_state.logged_in_acc = None

# --- HELPER FUNCTIONS ---
def generate_account_number():
    # Generates a random 10 digit account number starting with '9'
    while True:
        acc_num = '9' + ''.join([str(random.randint(0, 9)) for _ in range(9)])
        if acc_num not in st.session_state.db:
            return acc_num

def get_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --- APP LAYOUT ---
st.title("🏦 Apex Virtual Bank")
st.markdown("Secure, Fast, and Reliable Web Banking.")

# --- SIDEBAR NAVIGATION ---
menu = st.sidebar.radio("Navigation", ["Home / Login", "Open an Account"])

# ==========================================
# 1. ACCOUNT CREATION
# ==========================================
if menu == "Open an Account":
    st.header("Open a New Bank Account")
    st.write("Join us today and get your 10-digit account number instantly.")
    
    with st.container(border=True):
        new_name = st.text_input("Enter Your Full Name:")
        new_pin = st.text_input("Choose a 4-digit PIN:", type="password", max_chars=4)
        
        if st.button("Create My Account"):
            if not new_name or not new_pin:
                st.error("Please fill in all fields.")
            elif len(new_pin) != 4 or not new_pin.isdigit():
                st.error("PIN must be exactly 4 digits.")
            else:
                acc_num = generate_account_number()
                
                # Save to database
                st.session_state.db[acc_num] = {
                    "name": new_name,
                    "pin": new_pin,
                    "balance": 0.0,
                    "history": [f"[{get_time()}] Account created successfully."]
                }
                save_db(st.session_state.db) # Save to JSON file
                
                st.success("🎉 Account Created Successfully!")
                st.info(f"**Your Account Number is: {acc_num}**")
                st.warning("Please copy your Account Number and keep your PIN safe. You will need them to log in.")

# ==========================================
# 2. LOGIN SYSTEM
# ==========================================
elif menu == "Home / Login":
    
    # If no one is logged in, show Login Screen
    if st.session_state.logged_in_acc is None:
        st.header("Customer Login")
        with st.container(border=True):
            login_acc = st.text_input("10-Digit Account Number:")
            login_pin = st.text_input("Enter 4-digit PIN:", type="password", max_chars=4)
            
            if st.button("Secure Login"):
                if login_acc in st.session_state.db:
                    if st.session_state.db[login_acc]["pin"] == login_pin:
                        st.session_state.logged_in_acc = login_acc
                        st.rerun()
                    else:
                        st.error("Incorrect PIN.")
                else:
                    st.error("Account Number not found.")
                    
    # ==========================================
    # 3. USER DASHBOARD (Logged In)
    # ==========================================
    else:
        acc_num = st.session_state.logged_in_acc
        user_data = st.session_state.db[acc_num]
        
        # Dashboard Header
        st.subheader(f"Welcome back, {user_data['name']} 👋")
        st.markdown(f"**Account Number:** `{acc_num}`")
        
        # Display Balance
        st.metric(label="Available Balance", value=f"₦{user_data['balance']:,.2f}")
        
        # Action Tabs
        dep_tab, with_tab, trans_tab, hist_tab = st.tabs(["Deposit", "Withdraw", "Transfer", "History"])
        
        # --- DEPOSIT ---
        with dep_tab:
            st.write("Add funds to your account.")
            dep_amount = st.number_input("Amount to deposit (₦):", min_value=0.0, step=500.0, key="dep")
            if st.button("Deposit Funds"):
                if dep_amount > 0:
                    user_data['balance'] += dep_amount
                    user_data['history'].append(f"[{get_time()}] Deposited: +₦{dep_amount:,.2f}")
                    save_db(st.session_state.db)
                    st.success(f"Successfully deposited ₦{dep_amount:,.2f}")
                    st.rerun()
                    
        # --- WITHDRAW ---
        with with_tab:
            st.write("Withdraw funds from your account.")
            with_amount = st.number_input("Amount to withdraw (₦):", min_value=0.0, step=500.0, key="wit")
            with_pin = st.text_input("Confirm PIN:", type="password", max_chars=4, key="wit_pin")
            if st.button("Withdraw Funds"):
                if with_pin != user_data['pin']:
                    st.error("Incorrect PIN.")
                elif with_amount > user_data['balance']:
                    st.error("Insufficient funds.")
                elif with_amount > 0:
                    user_data['balance'] -= with_amount
                    user_data['history'].append(f"[{get_time()}] Withdrew: -₦{with_amount:,.2f}")
                    save_db(st.session_state.db)
                    st.success(f"Successfully withdrew ₦{with_amount:,.2f}")
                    st.rerun()
                    
        # --- TRANSFER ---
        with trans_tab:
            st.write("Send money to another Apex Bank user.")
            rec_acc = st.text_input("Receiver's 10-Digit Account Number:")
            trans_amount = st.number_input("Amount to send (₦):", min_value=0.0, step=500.0, key="trans")
            trans_pin = st.text_input("Confirm PIN:", type="password", max_chars=4, key="trans_pin")
            
            if st.button("Transfer Funds"):
                if trans_pin != user_data['pin']:
                    st.error("Incorrect PIN.")
                elif rec_acc not in st.session_state.db:
                    st.error("Receiver Account not found.")
                elif rec_acc == acc_num:
                    st.error("You cannot transfer to yourself.")
                elif trans_amount > user_data['balance']:
                    st.error("Insufficient funds for this transfer.")
                elif trans_amount > 0:
                    # Deduct from Sender
                    user_data['balance'] -= trans_amount
                    user_data['history'].append(f"[{get_time()}] Transfer to {rec_acc}: -₦{trans_amount:,.2f}")
                    
                    # Add to Receiver
                    st.session_state.db[rec_acc]['balance'] += trans_amount
                    st.session_state.db[rec_acc]['history'].append(f"[{get_time()}] Received from {acc_num}: +₦{trans_amount:,.2f}")
                    
                    save_db(st.session_state.db)
                    st.success(f"Successfully transferred ₦{trans_amount:,.2f} to {st.session_state.db[rec_acc]['name']}.")
                    st.rerun()
                    
        # --- HISTORY ---
        with hist_tab:
            st.write("Recent Transactions")
            with st.container(border=True):
                # Reverse history to show newest first
                for record in reversed(user_data['history']):
                    st.text(record)
                    
        st.divider()
        if st.button("Secure Log Out"):
            st.session_state.logged_in_acc = None
            st.rerun()
