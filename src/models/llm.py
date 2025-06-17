from langchain_deepseek import ChatDeepSeek
from .prompt import REACT_PROMPT, PLANNER_PROMPT, REPLANNER_PROMPT, get_tools_description
from langchain_core.prompts import ChatPromptTemplate
import os
import json
import streamlit as st
from datetime import datetime

def load_llm_config():
    """加载LLM配置文件"""
    try:
        with open('config/llm_config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"加载LLM配置文件失败: {str(e)}")
        return {}

def get_llm():
    """获取LLM实例，每次调用都会重新读取配置"""
    config = load_llm_config()
    deepseek_config = config.get('deepseek', {})
    
    # 设置环境变量
    os.environ["DEEPSEEK_API_KEY"] = deepseek_config.get('api_key', '')
    
    # 创建新的LLM实例
    return ChatDeepSeek(
        model=deepseek_config.get('model', 'deepseek-chat'),
        base_url=deepseek_config.get('base_url', 'https://api.deepseek.com'),
        api_key=deepseek_config.get('api_key', ''),
        temperature=deepseek_config.get('temperature', 0)
    )

def get_prompt(enabled_services):
    """根据启用的服务生成prompt"""
    timestamp = "current date is " + datetime.now().strftime('%Y-%m-%d')
    tools_description = get_tools_description(enabled_services)
    return timestamp+REACT_PROMPT.format(tools_description)

def get_planner_prompt():
    """获取规划器prompt"""
    timestamp = "current date is " + datetime.now().strftime('%Y-%m-%d')
    return ChatPromptTemplate.from_messages([
        ("system", timestamp+PLANNER_PROMPT),
        ("placeholder", "{messages}"),
    ])

def get_replanner_prompt():
    """获取重规划器prompt"""
    timestamp = "current date is " + datetime.now().strftime('%Y-%m-%d')
    return ChatPromptTemplate.from_template(timestamp+REPLANNER_PROMPT) 

