# packages
from datetime import datetime

# streamlit
import streamlit as st
from scripts.setting import default_setting, back_to_home
if "user_key" not in st.session_state:
    st.switch_page("app.py")

# contract
from scripts.contract import BlockInformation, Contract, private_key_to_account_address
user_key = st.session_state.user_key
user_address = private_key_to_account_address(user_key)
block_information = BlockInformation(wallet_secret_key = user_key)

# from call function
event_list = block_information.contract_creation

# isAlive == True and 你不是莊家 才可下注
# DEMO 先不卡控 已經截止的事件 不能下注
if len(event_list) > 0:
    event_list = [event for event in event_list if event["isAlive"]]
    event_list = [event for event in event_list if event["contract_manager"] != user_address]

# main page
default_setting()
st.markdown("## 📃活動列表")
back_to_home()

if len(event_list) == 0:
    st.markdown("### 目前沒有可以下注的活動")
else:
    for event in event_list:
        timestamp = event["timestamp"]
        contract_address = event["contract_address"]
        eventName = event["eventName"]
        options = event["Options"]
        dueDate = event["dueDate"]
        options = [option[1] for option in options]

        with st.expander(f'{timestamp.strftime("%Y-%m-%d %H:%M:%S")}~{datetime.fromtimestamp(dueDate).strftime("%Y-%m-%d %H:%M:%S")}' + " | " + eventName):
            with st.form(f"event_{contract_address}", border = False):
                # 選項
                select = st.radio("", options, horizontal = True)
                # 下注按鈕
                vote = st.form_submit_button("下注", use_container_width = True)
                if vote:
                    selection = options.index(select)
                    Contract(contract_address, wallet_secret_key = user_key).enter(selection)
                    st.success(f"你選擇「{select}」，祝你重大獎!!!")