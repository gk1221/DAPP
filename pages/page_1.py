# packages
import pandas as pd
import streamlit as st
from scripts.setting import default_setting, back_to_home
if "user_key" not in st.session_state:
    st.switch_page("app.py")

# contract
from scripts.contract import BlockInformation
user_key = st.session_state.user_key
block_information = BlockInformation(wallet_secret_key = user_key)

default_setting()

# from call function
event_list = pd.DataFrame(block_information.contract_creation)
event_list = event_list.rename(columns = {"contract_address": "to"})

# personal information
st.markdown("## 😀個人資訊")

back_to_home()

with st.expander("💰錢包資訊", expanded = True):

    st.write(f"你的錢包位址: {block_information.wallet_address}")
    eth = "{:,.0f}".format(block_information.wallet_balance)
    st.write(f"你的錢包餘額: {eth} ETH")

with st.expander("🎲已下注清單"):

    column_name = ["時間", "事件名稱", "下注選項", "下注金額"]
    df = block_information.action_log
    df = df.loc[(df["from"] == block_information.wallet_address) & (df["function_name"] == "enter")]
    if df.shape[0] == 0:
        st.dataframe(pd.DataFrame(columns = column_name), use_container_width = True, hide_index = True)
    else:
        df = df.merge(event_list, on = "to")
        df["selection"] = df["selection"].apply(lambda x : x["selection"])
        df["Options"] = df["Options"].apply(lambda options : [option[1] for option in options])
        df["selection"] = df.apply(lambda x : x["Options"][x["selection"]], axis = 1)
        df = df[["timestamp", "eventName", "selection", "value"]]
        df.columns = column_name
        st.dataframe(df, use_container_width = True, hide_index = True)
# st.write(st.session_state)