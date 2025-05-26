import streamlit as st
import asyncio
import sys
from datetime import datetime
from src.config.logger import output_logger
from src.workflow.agent import create_workflow
from web_app.web_logger import web_logger
from langchain_mcp_adapters.client import MultiServerMCPClient
# 设置 Windows 上的事件循环策略
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

def clear_previous_task():
    """清空上一个任务的内容"""
    if "messages" in st.session_state:
        st.session_state["messages"] = []

def add_clear_button():
    """添加一个清空按钮到界面"""
    if st.button("清空内容", help="清空当前页面内容，创建新任务"):
        clear_previous_task()
        st.rerun()

def pretty_print(event):
    """美化输出事件内容到网页"""
    if "planner" in event:
        st.session_state["messages"].append({"role": "assistant", "content": "【规划任务步骤】"})
        with st.chat_message("assistant"):
            st.markdown("### 【规划任务步骤】")
            for idx, step in enumerate(event["planner"]["plan"], 1):
                output_logger.log(f"{step}")
                st.session_state["messages"].append({"role": "assistant", "content": f"{step}"})
                st.markdown(f"{step}")
    
    if "agent" in event:
        output_logger.log("【执行结果】")
        st.session_state["messages"].append({"role": "assistant", "content": "【执行结果】"})
        with st.chat_message("assistant"):
            st.markdown("### 【执行结果】")
            for step, result in event["agent"]["past_steps"]:
                output_logger.log(f"步骤: {step}")
                output_logger.log(f"结果: {result}")
                st.session_state["messages"].append({"role": "assistant", "content": f"步骤: {step}\n结果: {result}"})
                #with st.chat_message("assistant"):
                st.markdown(f"步骤: {step}")
                st.markdown(f"结果: {result}")

    
    if "replan" in event:
        if "plan" in event["replan"]:
            output_logger.log("## 【重新规划任务】")
            st.session_state["messages"].append({"role": "assistant", "content": "【重新规划任务】"})
            with st.chat_message("assistant"):
                st.markdown("### 【重新规划任务】")
                for idx, step in enumerate(event["replan"]["plan"], 1):
                    output_logger.log(f"{step}")    
                    st.session_state["messages"].append({"role": "assistant", "content": f"{step}"})
                    st.markdown(f"{step}")  
        if "response" in event["replan"]:
            output_logger.log("【最终结果】")
            st.session_state["messages"].append({"role": "assistant", "content": "【最终结果】"})
            output_logger.log(f"{event['replan']['response']}")
            st.session_state["messages"].append({"role": "assistant", "content": f"【最终结果】\n{event['replan']['response']}"})
            with st.chat_message("assistant"):
                st.markdown("### 【最终结果】")
                st.markdown(f"{event['replan']['response']}")
                

def main():
    # 设置页面配置
    st.set_page_config(page_title="FengAgent Web Interface", layout="wide")

    # 设置标题
    st.title("🤖 FengAgent 智能体")

    # 初始化session state
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # 创建主容器
    with st.container():
        st.header("与 FengAgent 对话")
        st.markdown("FengAgent 是一个基于Deepseek LLM的Plan-execute架构智能体Agent，具有网页搜索、股票查询与分析、地图查询与导航等功能")
        st.markdown("Author: YYF <small>from CMS Fintech Centre</small>", unsafe_allow_html=True)

        # 添加清空按钮
        add_clear_button()
        
        # 显示历史消息
        for message in st.session_state["messages"]:
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.markdown(message["content"])
            else:
                with st.chat_message("assistant"):
                    st.markdown(message["content"])
        
        # 用户输入
        prompt = st.chat_input("请输入您的任务...")
        
        client = None
        client = MultiServerMCPClient(
            {
                "math": {
                    "command": "python",
                    "args": ["D:/YangYufeng/zs/lang_learn/adapter/math_server.py"],
                    "transport": "stdio",
                },
                "amap-amap-sse": {
                    "url": "https://mcp.amap.com/sse?key=1253cf9b3968fc48fd39b06b02fa5211",
                    "transport": "sse",
                },
                "tavily-mcp": {
                    "command": "npx",
                    "args": ["-y", "tavily-mcp"],
                    "env": {"TAVILY_API_KEY": "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"},
                    "autoApprove": []
                },
                "mcp-akshare": {
                    "command": "uvx",
                    "args": ["src/tool/mcp-akshare"],
                },
            }
        )
        tools = client.get_tools()

        if prompt:
            # 添加用户消息到历史记录
            st.session_state["messages"].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # 使用 asyncio 运行异步任务
            async def run_agent_async():
                workflow = create_workflow(tools)
                config = {"recursion_limit": 50}
                inputs = {"input": prompt}
                
                with st.spinner("FengAgent正在思考..."):
                    async for event in workflow.astream(inputs, config=config):
                        pretty_print(event)
            
            # 在 Streamlit 中运行异步代码
            asyncio.run(run_agent_async())

    # 添加侧边栏说明
    with st.sidebar:
        st.header("使用说明")
        st.markdown("""
        1. 在输入框中输入任务，如"帮我分析新能源领域的股票情况"
        2. FengAgent会分析您的问题并任务规划
        3. 在依次执行子任务的过程中，会基于当前任务结果进行重新规划            
        3. 您可以查看执行过程和最终结果
        4. 所有对话历史都会被保存
        5. 使用"清空内容"按钮可以清空当前页面所有内容
        """)

if __name__ == "__main__":
    main() 