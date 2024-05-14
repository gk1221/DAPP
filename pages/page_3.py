# packages
from datetime import datetime

# streamlit
import streamlit as st
from streamlit_tags import st_tags
from scripts.setting import default_setting, back_to_home
if "user_key" not in st.session_state:
    st.switch_page("app.py")

# contract
from scripts.contract import DeployContract, BlockInformation, Contract, private_key_to_account_address
user_key = st.session_state.user_key
user_address = private_key_to_account_address(user_key)
block_information = BlockInformation(wallet_secret_key = user_key)

# from call function
event_list = block_information.contract_creation

# 可以管理的事件: isAlive == True and 你是莊家
allow_contract_list = []
if len(event_list) > 0:
    for event in event_list:
        if event["isAlive"] == True and event["contract_manager"] == user_address:
            allow_contract_list.append(event["contract_address"])

# main page
default_setting()
st.markdown("## 👑活動管理")
back_to_home()

with st.expander("➕建立活動"):
    with st.form("create_event", border = False):
        # input
        title = st.text_input("事件名稱", placeholder = "必填")
        options = st_tags(label = "事件選項", text = "按 Enter 新增", value = [])
        deadline = st.date_input("截止日期")
        deadline = datetime(deadline.year, deadline.month, deadline.day)
        deadline = int(deadline.timestamp())

        # create button
        create = st.form_submit_button("建立", use_container_width = True)
        if create:
            if title == "":
                st.warning("請輸入事件名稱")
            elif len(options) < 2:
                st.warning("至少兩個選項")
            elif len(list(set(options))) != len(options):
                st.warning("有重複的選項，請確認")
            else:
                DeployContract(account_address = user_address,
                               name = title,
                               optionNames = options,
                               due = deadline).deploy()
                st.success(f"建立活動「{title}」成功")

with st.expander("👀檢視活動"):
    # 輸入正確答案 + 結算事件
    if len(event_list) == 0:
        st.markdown("### 目前還沒有任何活動")
    else:
        for event in event_list:   
            timestamp = event["timestamp"]
            contract_address = event["contract_address"]
            contract_manager = event["contract_manager"]
            eventName = event["eventName"]
            options = event["Options"]
            dueDate = event["dueDate"]
            isAlive = event["isAlive"]
            resultOption = event["resultOption"]
            options = [f"{option[1]}({option[2]}人下注)" for option in options]

            with st.form(key = f"event_{contract_address}"):
                st.write(timestamp.strftime("%Y-%m-%d %H:%M:%S") + " " + eventName)
                # options
                select = st.radio("請選擇正確答案", options, horizontal = True)
                
                # 還沒被結束的事件
                if isAlive:
                    
                     # 你不是莊家
                    if contract_manager != private_key_to_account_address(user_key):
                        vote = st.form_submit_button("你不是莊家", use_container_width = True, disabled = True)

                    # 時間到了，可以輸入正確答案結束活動
                    elif int(datetime.now().timestamp()) >= dueDate:
                        vote = st.form_submit_button("輸入正確答案結束活動", use_container_width = True)
                    
                    # 時間還沒到
                    else:
                        vote = st.form_submit_button("活動尚未截止", use_container_width = True, disabled = True)
                
                # 已經結束的事件
                else:
                    if resultOption == "":
                        vote = st.form_submit_button("該活動已被莊家取消", use_container_width = True, disabled = True)
                    else:
                        vote = st.form_submit_button(f"該活動已結束，正確答案是「{resultOption}」", use_container_width = True, disabled = True)

                # 輸入正確答案結束活動
                if vote:
                    selection = options.index(select)
                    Contract(contract_address, wallet_secret_key = user_key).endEvent(selection)
                    st.success(f"遊戲結束，最後獲勝者為選擇「{select}」")

with st.expander("➖取消活動"):
    if len(event_list) > 0:
        with st.form("cancel_event", border = False):
            # current active event name
            delete_event_list = [event["timestamp"].strftime("%Y-%m-%d %H:%M:%S") + " " + event["eventName"] for event in event_list if event["contract_address"] in allow_contract_list]
            delete_event = st.selectbox("選擇要取消的活動(只能取消自己建立的活動)", delete_event_list, index = 0)
            
            if len(delete_event_list) == 0:
                delete = st.form_submit_button("沒有可取消的活動", use_container_width = True, disabled = True)
            else:
                delete = st.form_submit_button("取消該活動", use_container_width = True)

            if delete:
                # 結束活動
                delete_index = delete_event_list.index(delete_event)

                contract = Contract(contract_address = allow_contract_list[delete_index],
                                    wallet_secret_key = user_key)

                contract.cancel()
                st.success(f"取消「{delete_event}」成功，將返還給每位玩家原下注金額。")
    else:
        st.markdown("### 目前還沒有任何活動")