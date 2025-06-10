import streamlit as st
import asyncio
import sys
from datetime import datetime
from src.config.logger import output_logger
from src.workflow.agent import create_workflow
from web_app.web_logger import web_logger
from langchain_mcp_adapters.client import MultiServerMCPClient
import json
import os

# 设置 Windows 上的事件循环策略
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

def check_api_key():
    """检查是否设置了API key"""
    config_path = os.path.join('config', 'llm_config.json')
    if not os.path.exists(config_path):
        return False
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return bool(config.get('deepseek', {}).get('api_key'))
    except:
        return False

def clear_previous_task():
    """清空上一个任务的内容"""
    if "messages" in st.session_state:
        st.session_state["messages"] = []

def add_clear_button():
    """添加一个清空按钮到界面"""
    if st.button("创建新任务", help="清空当前页面内容，创建新任务"):
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
        st.session_state["messages"].append({"role": "assistant", "content": "【执行结果】"})
        with st.chat_message("assistant"):
            st.markdown("### 【执行结果】")
            for step, result in event["agent"]["past_steps"]:
                output_logger.log(f"结果: {result}")
                st.session_state["messages"].append({"role": "assistant", "content": f"步骤: {step}\n结果: {result}"})
                st.markdown(f"结果:")
                st.markdown(f"{result}")
    
    if "replan" in event:
        if "plan" in event["replan"]:
            st.session_state["messages"].append({"role": "assistant", "content": "【重新规划任务】"})
            with st.chat_message("assistant"):
                st.markdown("### 【重新规划任务】")
                for idx, step in enumerate(event["replan"]["plan"], 1):
                    output_logger.log(f"{step}")    
                    st.session_state["messages"].append({"role": "assistant", "content": f"{step}"})
                    st.markdown(f"{step}")
        if "response" in event["replan"]:
            st.session_state["messages"].append({"role": "assistant", "content": "【最终结果】"})
            output_logger.log(f"{event['replan']['response']}")
            st.session_state["messages"].append({"role": "assistant", "content": f"{event['replan']['response']}"})
            with st.chat_message("assistant"):
                st.markdown("### 【最终结果】")
                st.markdown(f"{event['replan']['response']}")

def load_mcp_config():
    """加载MCP配置文件"""
    try:
        with open('config/mcp_config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"加载MCP配置文件失败: {str(e)}")
        return {}

def main():
    # 设置页面配置
    st.set_page_config(page_title="EasyAgent Web Interface", layout="wide")

    # 设置标题
    st.title("🤖 EasyAgent 智能体")

    # 初始化session state
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # 创建主容器
    with st.container():
        st.header("Welcome!")
        st.markdown("EasyAgent是一个基于langchain的Planning Agent，接入了网页搜索、股票查询、arxiv数据库等MCP工具")
        
        # 检查API key
        if not check_api_key():
            st.warning("⚠️ 请先在设置页面配置您的Deepseek API Key")
            st.markdown("请点击左侧导航栏的 🐋 Deepseek Settings 进行配置")
            return

        # 添加清空按钮
        add_clear_button()

        # 用户输入
        prompt = st.chat_input("请输入您的任务...")
        
        # 添加示例提示
        with st.expander("💡 点击查看任务示例 "):
            st.markdown("""
            **股票分析：**
            - 请帮我分析近期新能源股票的情况
            - 帮我获取比亚迪的涨跌情况
            - 分析一下近期的A股市场走势
            
            **查询搜索：**
            - 帮我搜索和总结近两年关于大模型的高被引论文
            - 目前热门的开源Agent框架有哪些？
            """)
        
        # 加载MCP配置
        mcp_config = load_mcp_config()
        client = MultiServerMCPClient(mcp_config)

        tools = client.get_tools()

        if prompt:
            # 清空之前的内容
            clear_previous_task()
            
            st.session_state["messages"].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # 使用 asyncio 运行异步任务
            async def run_agent_async():
                workflow = create_workflow(tools)
                config = {"recursion_limit": 50}
                inputs = {"input": prompt}
                
                with st.spinner("EasyAgent正在思考..."):
                    async for event in workflow.astream(inputs, config=config):
                        pretty_print(event)
            
            # 在 Streamlit 中运行异步代码
            asyncio.run(run_agent_async())


            """
            布局（五位一体、四个全面），改革（一制两治）、法治（两个建设）、经济（三新一高）、强军（听能作）、外交（国内世界）、治党（六个建设）
            """
    # 添加侧边栏说明
    with st.sidebar:
        st.header("Note")
        st.markdown("""
        1. 在输入框中输入，Agent会为您规划任务
        2. "EasyAgent正在思考..."表示任务仍在进行，非流式输出下响应时间可能较长
        3. 仅用于学习研究，不适用于实际交易
        """)
        st.markdown("---")
        st.markdown("<p style='font-size: 14px;'><strong>Author:</strong> YYF, u3621301@connect.hku.hk</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main() 