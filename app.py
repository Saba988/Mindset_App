import streamlit as st
import json
import os
import numpy as np
import pandas as pd

# --- Data Manager Class ---
class DataManager:
    def __init__(self, filepath='data.json'):
        self.filepath = filepath
        self.data = self.load_data()

    def load_data(self):
        if not os.path.exists(self.filepath):
            with open(self.filepath, 'w') as f:
                json.dump({}, f)
        with open(self.filepath, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}

    def save_data(self):
        with open(self.filepath, 'w') as f:
            json.dump(self.data, f, indent=4)

    def get_user(self, email):
        return self.data.get(email, None)

    def register_user(self, email):
        self.data[email] = {
            "wallet": 5,
            "mindcoins": 0,
            "active": [],
            "completed": []
        }
        self.save_data()

    def update_user(self, email, user_data):
        self.data[email] = user_data
        self.save_data()

# --- Challenge Bank ---
class Challenge:
    bank = [
        {"title": "Drink 8 glasses of water", "description": "Stay hydrated throughout the day", "reward": 5},
        {"title": "Read 10 pages of a book", "description": "Expand your knowledge", "reward": 7},
        {"title": "Exercise for 20 minutes", "description": "Move your body", "reward": 10},
        {"title": "Meditate for 10 minutes", "description": "Clear your mind", "reward": 8},
        {"title": "Write down 3 things you're grateful for", "description": "Practice gratitude", "reward": 6}
    ]

# --- Quotes Loader ---
def load_quotes(filepath='quotes.txt'):
    if not os.path.exists(filepath):
        with open(filepath, 'w') as f:
            f.write("Believe in yourself!\nNever give up!\nStay positive!")
    with open(filepath, 'r') as f:
        return f.read().splitlines()

# --- Main App ---
class MindsetApp:
    def __init__(self):
        self.dm = DataManager()
        self.quotes = load_quotes()
        self.run()

    def login_page(self):
        st.sidebar.subheader("Login to Continue")
        email = st.sidebar.text_input("Enter your Email")
        if st.sidebar.button("Login"):
            user = self.dm.get_user(email)
            if user:
                st.session_state['logged_in'] = True
                st.session_state['email'] = email
                st.rerun()
            else:
                st.error("Email not found. Please Register first.")

    def register_page(self):
        st.sidebar.subheader("Create a New Account")
        email = st.sidebar.text_input("Enter your Email for Registration")
        if st.sidebar.button("Register"):
            if self.dm.get_user(email):
                st.error("Account already exists!")
            else:
                self.dm.register_user(email)
                st.success("Account created successfully! Please Login now.")

    def dashboard(self, email):
        user = self.dm.get_user(email)
        st.success("Logged In Successfully!")
        st.subheader(f"Welcome back, {email} 👋")
        st.write(f"💵 Wallet Balance: ${user['wallet']}")
        st.write(f"🪙 MindCoins Earned: {user['mindcoins']}")

        st.subheader("Active Challenges")
        if not user['active']:
            st.info("No active challenges! Pick one below:")
            for ch in Challenge.bank:
                if st.button(f"Accept: {ch['title']}"):
                    if user['wallet'] >= 1:
                        user['wallet'] -= 1
                        user['active'].append(ch)
                        self.dm.update_user(email, user)
                        st.success("Challenge accepted!")
                        st.rerun()
                    else:
                        st.error("Not enough money to accept new challenge!")
        else:
            for idx, ch in enumerate(user['active']):
                st.write(f"🔵 {ch['title']}: {ch['description']}")
                if st.button(f"Mark '{ch['title']}' as Completed", key=f"complete_{idx}"):
                    user['active'].remove(ch)
                    user['completed'].append(ch)
                    user['mindcoins'] += ch['reward']
                    self.dm.update_user(email, user)
                    st.success("Challenge Completed and Reward Added!")
                    st.rerun()

        st.subheader("📜 Completed Challenges")
        if user['completed']:
            df = pd.DataFrame(user['completed'])
            st.dataframe(df)
        else:
            st.info("No challenges completed yet!")

        st.subheader("🌟 Motivational Quote of the Day")
        st.success(np.random.choice(self.quotes))

    def run(self):
        st.set_page_config(page_title="Mindset – $1 Challenge", page_icon="🧠")
        st.title("🧠 *MindSet – A $1 Investment in Yourself*")

        if 'logged_in' not in st.session_state:
            st.session_state['logged_in'] = False

        menu = st.sidebar.selectbox("Menu", ["Login", "Register"])
        if st.session_state['logged_in']:
            self.dashboard(st.session_state['email'])
        elif menu == "Login":
            self.login_page()
        elif menu == "Register":
            self.register_page()

# --- Run App ---
if __name__ == '__main__':
    MindsetApp()

