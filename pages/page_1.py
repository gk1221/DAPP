# packages
import pandas as pd

# streamlit
import streamlit as st
from scripts.setting import default_setting, back_to_home
if "user_key" not in st.session_state:
    st.switch_page("app.py")

# contract
from scripts.contract import BlockInformation
user_key = st.session_state.user_key
block_information = BlockInformation(wallet_secret_key = user_key)

# from call function
event_list = pd.DataFrame(block_information.contract_creation)

# main page
default_setting()
st.markdown("## 😀個人資訊")
back_to_home()

with st.expander("💰錢包資訊", expanded = True):
    st.write(f"你的錢包位址: {block_information.wallet_address}")
    eth = "{:,.0f}".format(block_information.wallet_balance)
    st.write(f"你的錢包餘額: {eth} ETH")

with st.expander("🎲已下注清單"):
    column_name = ["時間", "事件名稱", "下注選項", "正確答案", "下注金額"]
    df = block_information.action_log
    df = df.rename(columns = {"to": "contract_address"})

    # 用 contract address 合併
    df = df.merge(event_list.drop(columns = "timestamp"), on = "contract_address")

    # 你自己的下注
    df = df.loc[(df["from"] == block_information.wallet_address) & (df["function_name"] == "enter")]
    if df.shape[0] != 0:
        df["selection"] = df["selection"].apply(lambda x : x["selection"])
        df["Options"] = df["Options"].apply(lambda options : [option[1] for option in options])
        df["selection"] = df.apply(lambda x : x["Options"][x["selection"]], axis = 1)
        df = df[["timestamp", "eventName", "selection", "resultOption", "value"]]
        df.columns = column_name
    # 沒有下注
    else:
        df = pd.DataFrame(columns = column_name)
    
    st.dataframe(df, use_container_width = True, hide_index = True)