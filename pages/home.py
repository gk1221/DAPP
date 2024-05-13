# packages
import streamlit as st
from scripts.setting import default_setting, button_setting, back_to_login
if "user_key" not in st.session_state:
    st.switch_page("app.py")

default_setting()
button_setting()

# title
st.title("🤑未來事件交易所🤑")

back_to_login()

# layout
col1, col2, col3 = st.columns(3)

if col1.button("# 😀個人資訊", use_container_width = True, type = "primary"):
    st.switch_page("pages/page_1.py")

if col2.button("# 📃活動列表", use_container_width = True, type = "primary"):
    st.switch_page("pages/page_2.py")

if col3.button("# 👑活動管理", use_container_width = True, type = "primary"):
    st.switch_page("pages/page_3.py")

# st.write(st.session_state)