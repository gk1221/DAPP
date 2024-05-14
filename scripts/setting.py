import streamlit as st
from configparser import ConfigParser

def default_setting():
    # streamlit setting
    st.set_page_config(
        page_title = "未來事件交易所",
        layout = "wide",
        initial_sidebar_state = "collapsed",
        page_icon = ":moneybag:")

    st.markdown(
        """
        <style>
        [data-testid="collapsedControl"] {
            display: none
        }
        </style>
        """, unsafe_allow_html = True)
    
def button_setting():
    st.markdown(
    """
    <style>
    button[kind="primary"] {
        padding-top: 200px !important;
        padding-bottom: 200px !important;
        font-size: 50px;
        color: white;
        background-color: #4e79a7;
        border-color: #4e79a7;
    }
    button:hover[kind="primary"] {
        color: black;
        background-color: #a0cbe8;
        border-color: #a0cbe8;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

def back_to_home():
    if st.button("返回首頁", use_container_width = True):
        st.switch_page("pages/home.py")
    
def back_to_login():
    if st.button("重新連結錢包", use_container_width = True):
        st.switch_page("app.py")

def get_path(name):
    config = ConfigParser()
    config.read("./config.ini")
    return config["source"][name]