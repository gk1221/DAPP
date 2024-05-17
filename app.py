# packages
import streamlit as st
from scripts.setting import default_setting, button_setting

default_setting()

# title
st.title("🤑未來事件交易所🤑")

with st.form("join", border = False):
    user_key = st.text_input("Input your wallet private key: ", type = "password")
    join = st.form_submit_button("🔗連結錢包", use_container_width = True)
    if join:
        st.session_state["user_key"] = user_key
        st.switch_page("pages/home.py")