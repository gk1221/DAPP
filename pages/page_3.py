# streamlit
import streamlit as st
from streamlit_tags import st_tags
from scripts.setting import default_setting, back_to_home
if "user_key" not in st.session_state:
    st.switch_page("app.py")

# contract
from scripts.contract import DeployContract, BlockInformation, Contract, private_key_to_account_address
user_key = st.session_state.user_key
block_information = BlockInformation(wallet_secret_key = user_key)

# common use
from datetime import datetime
import pandas as pd

default_setting()

# from call function
event_list = block_information.contract_creation

# contract allow manage
allow_contract_list = []
if len(event_list) > 0:
    for event in event_list:
        # still alive and manager is you
        if event["isAlive"] == True and event["contract_manager"] == private_key_to_account_address(user_key):
            allow_contract_list.append(event["contract_address"])

# event manage
st.markdown("## 👑活動管理")

back_to_home()

with st.expander("➕建立活動"):

    with st.form("create_event", border = False):
        # event name, options and deadline
        title = st.text_input("事件名稱", placeholder = "必填")
        options = st_tags(label = "事件選項", text = "按 Enter 新增", value = [])
        deadline = st.date_input("截止日期", min_value = datetime.now())
        deadline = datetime(deadline.year, deadline.month, deadline.day)
        deadline = int(deadline.timestamp())

        create = st.form_submit_button("建立", use_container_width = True)
        if create:
            if title == "":
                st.warning("請輸入事件名稱")
            elif len(options) < 2:
                st.warning("至少兩個選項")
            elif len(list(set(options))) != len(options):
                st.warning("有重複的選項，請確認")
            else:
                post_data = {"title": title, "options": options, "deadline": deadline}
                DeployContract(account_address = private_key_to_account_address(user_key),
                               name = title,
                               optionNames = options,
                               due = deadline).deploy()
                st.success("建立活動", title, "成功")

with st.expander("👀檢視活動"):
    # 輸入正確答案 + 結算事件
    df = pd.DataFrame(block_information.contract_creation)
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
            options = [f"{option[1]}({option[2]}人下注)" for option in options]

            with st.form(key = f"event_{contract_address}"):
                st.write(timestamp.strftime("%Y-%m-%d %H:%M:%S") + " " + eventName)
                # options
                select = st.radio("請選擇正確答案", options, horizontal = True)

                if isAlive:
                    if int(datetime.now().timestamp()) >= dueDate:
                        vote = st.form_submit_button("輸入正確答案結束活動", use_container_width = True)
                    else:
                        vote = st.form_submit_button("活動尚未截止", use_container_width = True, disabled = True)
                else:
                    vote = st.form_submit_button("該活動已結束", use_container_width = True, disabled = True)

                # enter event
                if vote:
                    selection = options.index(select)
                    contract = Contract(contract_address, wallet_secret_key = user_key)
                    contract.endEvent(selection)
                    st.success("遊戲結束，最後獲勝者為選擇「", select, "」")

with st.expander("➖取消活動"):

    if len(event_list) > 0:

        with st.form("delete_event", border = False):
            # current active event name
            delete_event_list = [event["timestamp"].strftime("%Y-%m-%d %H:%M:%S") + " " + event["eventName"] for event in event_list if event["contract_address"] in allow_contract_list]
            delete_event = st.selectbox("選擇要刪除的活動(只能取消自己建立的活動)", delete_event_list, index = 0)
            
            if len(delete_event_list) == 0:
                delete = st.form_submit_button("沒有可刪除的活動", use_container_width = True)
            else:
                delete = st.form_submit_button("刪除該活動", use_container_width = True)

            if delete:
                # 結束活動
                delete_index = delete_event_list.index(delete_event)

                contract = Contract(contract_address = allow_contract_list[delete_index],
                                    wallet_secret_key = user_key)

                contract.cancel()
                st.success("刪除「", delete_event, "」成功，將返還給每位玩家原下注金額。")
    else:
        st.markdown("### 目前還沒有任何活動")

# st.write(st.session_state)