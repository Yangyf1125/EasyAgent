import streamlit as st
import asyncio
import sys
from datetime import datetime
from src.workflow.agent import create_workflow

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
    
def if_api_valid():
    config_path = os.path.join('config', 'llm_config.json')
    if not os.path.exists(config_path):
        return False
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
        api_key = config.get('deepseek', {}).get('api_key')
    return api_key.startswith('sk-')

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
                st.session_state["messages"].append({"role": "assistant", "content": f"{step}"})
                st.markdown(f"{step}")
    
    if "agent" in event:
        st.session_state["messages"].append({"role": "assistant", "content": "【执行结果】"})
        with st.chat_message("assistant"):
            st.markdown("### 【步骤执行结果】")
            for step, result in event["agent"]["past_steps"]:
                st.session_state["messages"].append({"role": "assistant", "content": f"步骤: {step}\n结果: {result}"})
                st.markdown(f"结果:")
                st.markdown(f"{result}")
    
    if "replan" in event:
        if "plan" in event["replan"]:
            st.session_state["messages"].append({"role": "assistant", "content": "【重新规划任务】"})
            with st.chat_message("assistant"):
                st.markdown("### 【重新规划任务】")
                for idx, step in enumerate(event["replan"]["plan"], 1):
                    st.session_state["messages"].append({"role": "assistant", "content": f"{step}"})
                    st.markdown(f"{step}")
        if "response" in event["replan"]:
            st.session_state["messages"].append({"role": "assistant", "content": "【最终结果】"})
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

def get_mcp_service_descriptions():
    """获取MCP服务的描述信息"""
    return {
        "mcp-akshare": "A股数据查询",
        "akshare-one-mcp": "A股金融数据服务",
        "mcp-yahoo-finance": "雅虎财经服务",
        "tavily-mcp": "tavily网页搜索服务",
        "amap-amap-sse": "高德地理信息",
        "bing-cn-mcp-server": "必应中文搜索",

        "fetch": "网页内容获取服务",
        "arxiv-mcp-server": "学术论文库",
        "python-repl": "Python代码执行"
    }

def initialize_service_states():
    """初始化所有服务的状态为启用"""
    service_descriptions = get_mcp_service_descriptions()
    for service in service_descriptions.keys():
        if f"service_{service}" not in st.session_state:
            st.session_state[f"service_{service}"] = True

def get_selected_services():
    """获取选中的服务列表"""
    service_descriptions = get_mcp_service_descriptions()
    return [
        service for service in service_descriptions.keys()
        if st.session_state.get(f"service_{service}", True)
    ]

def main():
    # 设置页面配置
    st.set_page_config(page_title="EasyAgent Web Interface", layout="wide")

    # 设置标题
    st.title("🤖 EasyAgent 智能体")

    # 初始化session state
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    
    # 初始化服务状态
    initialize_service_states()

    # 创建一个空的占位符用于显示加载状态
    loading_placeholder = st.empty()

    # 创建主容器
    with st.container():
        st.header("Welcome!")
        st.markdown("EasyAgent是一个基于langchain的Planning Agent，接入了网页搜索、股票查询、arxiv数据库等MCP工具")
        
        # 检查API key
        if not check_api_key():
            st.warning("⚠️ 请先在设置页面配置您的Deepseek API Key\n\n请点击左侧导航栏的 🐋 Deepseek 进行配置")
            return
        if not if_api_valid():
            st.warning("⚠️ 请设置格式正确的Deepseek API Key，例如sk-xxxxxxx\n\n请点击左侧导航栏的 🐋 Deepseek 进行配置")
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
        
        # 获取选中的服务
        selected_services = get_selected_services()
        
        # 只保留选中的服务配置
        filtered_config = {
            service: config 
            for service, config in mcp_config.items() 
            if service in selected_services
        }
        
        client = MultiServerMCPClient(filtered_config)
        tools = client.get_tools()

        if prompt:
            # 清空之前的内容
            clear_previous_task()
            
            st.session_state["messages"].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # 初始化工作流
            workflow = create_workflow(tools, get_selected_services())
            
            # 使用 asyncio 运行异步任务
            async def run_agent_async():
                config = {"recursion_limit": 50}
                inputs = {"input": prompt}
                
                # 在右下角显示加载提示
                with loading_placeholder.container():
                    st.markdown("""
                    <style>
                    .loading-container {
                        position: fixed;
                        bottom: 20px;
                        right: 20px;
                        background-color: var(--background-color, rgba(255, 255, 255, 0.9));
                        color: var(--text-color, #262730);
                        padding: 10px 20px;
                        border-radius: 10px;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                        z-index: 1000;
                    }
                    /* 深色主题 */
                    @media (prefers-color-scheme: dark) {
                        .loading-container {
                            --background-color: rgba(38, 39, 48, 0.9);
                            --text-color: #ffffff;
                        }
                    }
                    /* 浅色主题 */
                    @media (prefers-color-scheme: light) {
                        .loading-container {
                            --background-color: rgba(255, 255, 255, 0.9);
                            --text-color: #262730;
                        }
                    }
                    </style>
                    <div class="loading-container">
                        🤔 EasyAgent正在思考...
                    </div>
                    """, unsafe_allow_html=True)
                
                with st.spinner("EasyAgent正在思考..."):
                    async for event in workflow.astream(inputs, config=config):
                        pretty_print(event)
                
                # 完成后清除加载提示
                loading_placeholder.empty()
            
            # 在 Streamlit 中运行异步代码
            asyncio.run(run_agent_async())

    # 添加侧边栏说明
    with st.sidebar:
        st.header("使用说明")
        st.markdown("""
        1. 在输入框中输入，Agent会为您规划任务
        2. 非流式输出下响应时间可能较长
        3. 仅用于学习研究，不适用于实际交易
        """)
        #st.warning("⚠️ 暂时仅支持deepseek")
        #st.markdown("----")
        st.markdown("<p style='font-size: 14px;'><strong>Author:</strong> YYF, u3621301@connect.hku.hk</p>", unsafe_allow_html=True)
        st.markdown("----")
        # 使用expander包装MCP服务设置
        with st.expander("🔧 MCP服务设置", expanded=False):
            st.markdown("### 选择要启用的MCP服务：")
            service_descriptions = get_mcp_service_descriptions()
            
            # 初始化所有服务的状态
            initialize_service_states()
            
            # 为每个服务创建开关
            for service, description in service_descriptions.items():
                st.toggle(
                    f"{service} - {description}",
                    key=f"service_{service}"
                )
            
            st.markdown("所有远程托管MCP使用的均是限额的默认API_KEY\n\n如遇问题或需添加其他工具，请在mcp_config.json中修改")

if __name__ == "__main__":
    main() 