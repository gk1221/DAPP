# packages
import streamlit as st
from scripts.setting import default_setting, back_to_home
if "user_key" not in st.session_state:
    st.switch_page("app.py")

# contract
from scripts.contract import BlockInformation, Contract
user_key = st.session_state.user_key
block_information = BlockInformation(wallet_secret_key = user_key)

# common use
from datetime import datetime

default_setting()

# from call function
event_list = block_information.contract_creation

# isAlive == True, 才可下注
if len(event_list) > 0:
    event_list = [event for event in event_list if event["isAlive"]]

# event list
st.markdown("## 📃活動列表")

back_to_home()

if len(event_list) == 0:
    st.markdown("### 目前還沒有任何活動")
else:
    for event in event_list:
        timestamp = event["timestamp"]
        contract_address = event["contract_address"]
        eventName = event["eventName"]
        options = event["Options"]
        dueDate = event["dueDate"]
        isAlive = event["isAlive"]
        options = [option[1] for option in options]

        with st.expander(f'{timestamp.strftime("%Y-%m-%d %H:%M:%S")}~{datetime.fromtimestamp(dueDate).strftime("%Y-%m-%d %H:%M:%S")}' + " | " + eventName):
            with st.form(f"event_{contract_address}", border = False):

                # options
                select = st.radio("", options, horizontal = True)
                vote = st.form_submit_button("下注", use_container_width = True)

                # enter event
                if vote:
                    selection = options.index(select)
                    contract = Contract(contract_address, wallet_secret_key = user_key)
                    contract.enter(selection)
                    st.write("你選擇", select, "，祝你重大獎!!!")

# st.write(st.session_state)