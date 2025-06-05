from langchain_deepseek import ChatDeepSeek
from .prompt2 import REACT_PROMPT, PLANNER_PROMPT, REPLANNER_PROMPT
from langchain_core.prompts import ChatPromptTemplate
import os
import streamlit as st



os.environ["DEEPSEEK_API_KEY"] = "sk-95de50fc5a6744a8bb766e4b1e53af7c"


llm = ChatDeepSeek(
    model="deepseek-chat", 
    base_url="https://api.deepseek.com",
    api_key="sk-95de50fc5a6744a8bb766e4b1e53af7c",
    temperature=0
)


# 初始化提示词模板
prompt = REACT_PROMPT

planner_prompt = ChatPromptTemplate.from_messages([
    ("system", PLANNER_PROMPT),
    ("placeholder", "{messages}"),
])

replanner_prompt = ChatPromptTemplate.from_template(REPLANNER_PROMPT) 