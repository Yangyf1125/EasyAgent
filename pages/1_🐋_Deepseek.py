import streamlit as st
import json
import os

def load_config():
    """从配置文件加载设置"""
    try:
        config_path = os.path.join('config', 'llm_config.json')
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('deepseek', {})
    except:
        pass
    return {
        "api_key": "",
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
        "temperature": 0.0
    }

def save_config(config_data):
    """保存配置到文件"""
    config_dir = "config"
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
        
    config_path = os.path.join(config_dir, "llm_config.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump({"deepseek": config_data}, f, indent=4)

# 初始化session state
if "DEEPSEEK_CONFIG" not in st.session_state:
    st.session_state["DEEPSEEK_CONFIG"] = load_config()

st.set_page_config(page_title="Deepseek Settings", layout="wide")

st.title("Deepseek Settings")

# 创建表单
with st.form(key="deepseek_settings_form"):
    # 使用session_state来控制输入框的值
    # api_key = st.text_input(
    #     "API Key", 
    #     value=st.session_state["DEEPSEEK_CONFIG"]["api_key"],
    #     #type="password",
    #     disabled=True,
    #     help="输入您的Deepseek API密钥"
    # )
    
    # 显示当前API key的最后6位
    current_api_key = st.session_state["DEEPSEEK_CONFIG"]["api_key"]
    if current_api_key:
        masked_key = "****" + current_api_key[-6:] if len(current_api_key) >= 6 else "****" + current_api_key
        st.caption(f"当前使用的API Key: {masked_key},公共web无需修改api_key")
    
    base_url = st.text_input(
        "Base URL",
        value=st.session_state["DEEPSEEK_CONFIG"]["base_url"],
        disabled=True,  # 设置为只读
        help="Deepseek API的基础URL（不可修改）"
    )
    
    model = st.text_input(
        "Model",
        value=st.session_state["DEEPSEEK_CONFIG"]["model"],
        disabled=True,  # 设置为只读
        help="要使用的模型名称（不可修改）"
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
    
    # 添加保存按钮
    col1, col2 = st.columns(2)
    with col1:
        submit_button = st.form_submit_button(label="保存设置")
    with col2:
        use_default_button = st.form_submit_button(label="使用默认API Key")
    
    if submit_button:
        # 更新session state
        st.session_state["DEEPSEEK_CONFIG"] = {
            "api_key": "sk-a31ca91a3d624c27a9406d9a9596b882",
            "base_url": "https://api.deepseek.com",  # 保持默认值
            "model": "deepseek-chat",  # 保持默认值
            "temperature": float(temperature)  # 确保保存的是float类型
        }
        
        # 保存到配置文件
        save_config(st.session_state["DEEPSEEK_CONFIG"])
        
        st.success("设置已保存！")
        st.rerun()  # 重新加载页面以更新显示
    
    if use_default_button:
        default_config = {
            "api_key": "sk-a31ca91a3d624c27a9406d9a9596b882",
            "base_url": "https://api.deepseek.com",
            "model": "deepseek-chat",
            "temperature": 0.0
        }
        st.session_state["DEEPSEEK_CONFIG"] = default_config
        save_config(default_config)
        st.success("已切换到默认API Key！")
        st.rerun()
