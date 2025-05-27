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
                #output_logger.log(f"步骤: {step}")
                output_logger.log(f"结果: {result}")
                st.session_state["messages"].append({"role": "assistant", "content": f"步骤: {step}\n结果: {result}"})
                #st.markdown(f"步骤: {step}")
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
        #st.markdown("Author: YYF <small>from CMS Fintech Centre</small>", unsafe_allow_html=True)
        st.markdown("<small>api_key设置页面尚未完善，目前默认使用Deepseek-V3</small>", unsafe_allow_html=True)

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
        
        client = None
        client = MultiServerMCPClient(
            {
                # "math": {
                #     "command": "python",
                #     "args": ["D:/YangYufeng/zs/lang_learn/adapter/math_server.py"],
                #     "transport": "stdio",
                # },
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
                "bing-cn-mcp-server": {
                    "type": "sse",
                    "url": "https://mcp.api-inference.modelscope.cn/sse/bf53f78667f54f"
                    },
                "akshare-one-mcp": {
                    "type": "sse",
                    "url": "https://mcp.api-inference.modelscope.cn/sse/2546d617f8e445"
                    },

                "mcp-yahoo-finance": {
                    "type": "sse",
                    "url": "https://mcp.api-inference.modelscope.cn/sse/44b98b6a7e8046"
                    },
                "fetch": {
                    "type": "sse",
                    "url": "https://mcp.api-inference.modelscope.cn/sse/5c537afd52804f"
                    },

                "arxiv-mcp-server": {
                    "type": "sse",
                    "url": "https://mcp.api-inference.modelscope.cn/sse/5da5bf0f0c604d"
                    },
                "mcp-server-chart": {
                    "type": "sse",
                    "url": "https://mcp.api-inference.modelscope.cn/sse/2b2af34ca5794a"
                    },
                "python-repl": {
                    "command": "uv",
                    "args": [
                        "--directory",
                        "/src/tool/mcp-python",
                        "run",
                        "mcp_python"
                    ]
                    },
                

            }

            
        )
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

    # 添加侧边栏说明
    with st.sidebar:
        st.header("Note")
        st.markdown("""
        1. 在输入框中输入，Agent会为您规划任务
        2. "EasyAgent正在思考..."表示任务仍在进行，非流式输出下响应时间可能较长
        3. 仅用于学习研究，不适用于实际交易
        """)
        st.markdown("---")
        #st.markdown("<p style='font-size: 14px;'><strong>Author:</strong> YYF, Intern from CMS Fintech Centre</p>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 14px;'><strong>Author:</strong> YYF, u3621301@connect.hku.hk</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main() 