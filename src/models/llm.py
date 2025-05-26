from langchain_deepseek import ChatDeepSeek
from .prompt import REACT_PROMPT, PLANNER_PROMPT, REPLANNER_PROMPT
from langchain_core.prompts import ChatPromptTemplate
import os



os.environ["DEEPSEEK_API_KEY"] = "sk-2574248e129a44cbbb543c8ffcceeec8"


llm = ChatDeepSeek(
    model="deepseek-chat", 
    base_url="https://api.deepseek.com",
    api_key="sk-2574248e129a44cbbb543c8ffcceeec8",
    temperature=0
)


# 初始化提示词模板
prompt = REACT_PROMPT

planner_prompt = ChatPromptTemplate.from_messages([
    ("system", PLANNER_PROMPT),
    ("placeholder", "{messages}"),
])

replanner_prompt = ChatPromptTemplate.from_template(REPLANNER_PROMPT) 