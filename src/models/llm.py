from langchain_deepseek import ChatDeepSeek
from .prompt2 import REACT_PROMPT, PLANNER_PROMPT, REPLANNER_PROMPT
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

# 初始化提示词模板
prompt = REACT_PROMPT

planner_prompt = ChatPromptTemplate.from_messages([
    ("system", PLANNER_PROMPT),
    ("placeholder", "{messages}"),
])

replanner_prompt = ChatPromptTemplate.from_template(REPLANNER_PROMPT) 