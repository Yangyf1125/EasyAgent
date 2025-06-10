import streamlit as st
import json
import os

# 初始化session state
if "DEEPSEEK_CONFIG" not in st.session_state:
    st.session_state["DEEPSEEK_CONFIG"] = {
        "api_key": "",
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
        "temperature": 0.0  # 确保temperature是float类型
    }

st.set_page_config(page_title="Deepseek Settings", layout="wide")

st.title("Deepseek Settings")

# 创建表单
with st.form(key="deepseek_settings_form"):
    api_key = st.text_input(
        "API Key", 
        value=st.session_state["DEEPSEEK_CONFIG"]["api_key"],
        type="password",
        help="输入您的Deepseek API密钥"
    )
    
    base_url = st.text_input(
        "Base URL",
        value=st.session_state["DEEPSEEK_CONFIG"]["base_url"],
        help="Deepseek API的基础URL"
    )
    
    model = st.text_input(
        "Model",
        value=st.session_state["DEEPSEEK_CONFIG"]["model"],
        help="要使用的模型名称"
    )
    
    # 确保temperature是float类型
    current_temperature = float(st.session_state["DEEPSEEK_CONFIG"]["temperature"])
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=current_temperature,
        step=0.1,
        help="控制输出的随机性，0表示最确定性，1表示最随机"
    )
    




    
    # 添加提交按钮
    submit_button = st.form_submit_button(label="保存设置")
    
    if submit_button:
        # 更新session state
        st.session_state["DEEPSEEK_CONFIG"] = {
            "api_key": api_key,
            "base_url": base_url,
            "model": model,
            "temperature": float(temperature)  # 确保保存的是float类型
        }
        
        # 保存到配置文件
        config_dir = "config"
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
            
        config_path = os.path.join(config_dir, "llm_config.json")
        config_data = {
            "deepseek": st.session_state["DEEPSEEK_CONFIG"]
        }
        
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4)
        
        st.success("设置已保存！")
