import streamlit as st

if "DEEPSEEK_API_KEY" not in st.session_state:
    st.session_state["DEEPSEEK_API_KEY"] = ""

if "DEEPSEEK_BASE_URL" not in st.session_state:
    st.session_state["DEEPSEEK_BASE_URL"] = ""

st.set_page_config(page_title="Deepseek Settings", layout="wide")

st.title("Deepseek Settings")

deepseek_api_key = st.text_input("API Key", value=st.session_state["DEEPSEEK_API_KEY"], max_chars=None, key=None, type='default')
deepseek_base_url = st.text_input("base_url", value=st.session_state["DEEPSEEK_BASE_URL"], max_chars=None, key=None, type='default')

saved = st.button("Save")

if saved:
    st.session_state["DEEPSEEK_API_KEY"] = deepseek_api_key 
    st.session_state["DEEPSEEK_BASE_URL"] = deepseek_base_url