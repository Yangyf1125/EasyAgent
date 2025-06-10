from langchain_deepseek import ChatDeepSeek
from .prompt import REACT_PROMPT, PLANNER_PROMPT, REPLANNER_PROMPT, get_tools_description
from langchain_core.prompts import ChatPromptTemplate
import os
import json
import streamlit as st

def load_llm_config():
    """加载LLM配置文件"""
    try:
        with open('config/llm_config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"加载LLM配置文件失败: {str(e)}")
        return {}

# 加载配置
config = load_llm_config()
deepseek_config = config.get('deepseek', {})

# 设置环境变量
os.environ["DEEPSEEK_API_KEY"] = deepseek_config.get('api_key', '')

# 初始化LLM
llm = ChatDeepSeek(
    model=deepseek_config.get('model', 'deepseek-chat'),
    base_url=deepseek_config.get('base_url', 'https://api.deepseek.com'),
    api_key=deepseek_config.get('api_key', ''),
    temperature=deepseek_config.get('temperature', 0)
)

def get_prompt(enabled_services):
    """根据启用的服务生成prompt"""
    tools_description = get_tools_description(enabled_services)
    return REACT_PROMPT.format(tools_description)

def get_planner_prompt():
    """获取规划器prompt"""
    return ChatPromptTemplate.from_messages([
        ("system", PLANNER_PROMPT),
        ("placeholder", "{messages}"),
    ])

def get_replanner_prompt():
    """获取重规划器prompt"""
    return ChatPromptTemplate.from_template(REPLANNER_PROMPT) 