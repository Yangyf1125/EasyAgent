import os, operator, signal, logging,asyncio,threading,traceback,sys
from datetime import datetime
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field
from typing import Annotated, List, Tuple,Union
from typing_extensions import TypedDict
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END,StateGraph, START
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
import streamlit as st
os.environ["DEEPSEEK_API_KEY"] = "sk-2574248e129a44cbbb543c8ffcceeec8"
from prompt import REACT_PROMPT, REACT_PROMPT_CH, PLANNER_PROMPT, PLANNER_PROMPT_CH, REPLANNER_PROMPT
from langchain_deepseek import ChatDeepSeek
# 设置 Windows 上的事件循环策略
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

class OutputLogger:
    def __init__(self, log_file='execution_log.txt'):
        self.log_file = log_file
        self._setup_logger()
        
    def _setup_logger(self):
        """设置日志记录器"""
        self.logger = logging.getLogger('execution_logger')
        self.logger.setLevel(logging.INFO)
        
        # 创建文件处理器，指定UTF-8编码
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # 设置日志格式
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # 添加处理器
        self.logger.addHandler(file_handler)
        
    def log(self, message):
        """记录日志信息"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"{timestamp} - {message}"
        self.logger.info(log_message)
        print(log_message)  # 同时输出到控制台

# 初始化全局日志记录器
output_logger = OutputLogger()

# 配置连接日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='mcp_connection.log'
)

# 加载环境变量
# load_dotenv()
# api_key = os.getenv("DEEPSEEK_API_KEY")


llm = ChatDeepSeek(model="deepseek-chat", base_url="https://api.deepseek.com",api_key="sk-2574248e129a44cbbb543c8ffcceeec8",temperature=0)
base_llm = ChatDeepSeek(model="deepseek-chat", base_url="https://api.deepseek.com", 
                       api_key="sk-2574248e129a44cbbb543c8ffcceeec8", temperature=0)
prompt = REACT_PROMPT

class PlanExecute(TypedDict):
    input: str
    plan: List[str]
    past_steps: Annotated[List[Tuple], operator.add]
    response: str

class Plan(BaseModel):
    """Plan to follow in future"""
    steps: List[str] = Field(
        description="different steps to follow, should be in sorted order"
    )

class Response(BaseModel):
    """Response to user."""
    response: str

class Act(BaseModel):
    """Action to perform."""
    action: Union[Response, Plan] = Field(
        description="Action to perform. If you want to respond to user, use Response. "
        "If you need to further use tools to get the answer, use Plan."
    )

def clear_previous_task():
    """
    清空上一个任务的内容
    保留用户输入框和基本界面元素
    """
    # 获取当前消息列表
    # if "messages" in st.session_state:
    #     # 只保留第一条消息（如果有的话）
    #     if len(st.session_state["messages"]) > 0:
    #         first_message = st.session_state["messages"][0]
    #         st.session_state["messages"] = [first_message]
    #     else:
    #         st.session_state["messages"] = []
    
    if "messages" in st.session_state:
        # 只保留第一条消息（如果有的话）
        if len(st.session_state["messages"]) > 0:
            st.session_state["messages"] = []

def add_clear_button():
    """
    添加一个清空按钮到界面
    """
    if st.button("清空内容", help="清空当前页面内容，创建新任务"):
        clear_previous_task()
        st.rerun()  # 重新运行应用以更新界面

# 设置页面配置
st.set_page_config(page_title="FengAgent Web Interface", layout="wide")

# 设置标题
st.title("🤖 FengAgent 智能体")

# 初始化session state
if "messages" not in st.session_state:
    st.session_state["messages"] = []

    if threading.current_thread() is threading.main_thread():
        signal.signal(signal.SIGINT, handle_interrupt)
        signal.signal(signal.SIGTERM, handle_interrupt)

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
            "args": ["D:/Github/mcp-akshare"]
        },
    }
)
output_logger.log("MCP客户端初始化完成")
tools = client.get_tools()
agent_executor = create_react_agent("deepseek:deepseek-chat", tools, prompt=prompt)

planner_prompt = ChatPromptTemplate.from_messages([
    ("system", PLANNER_PROMPT),
    ("placeholder", "{messages}"),
])
planner = planner_prompt | base_llm.with_structured_output(Plan)

replanner_prompt = ChatPromptTemplate.from_template(
    """For the given objective, analyze the current progress and generate the next actionable step. \
    Each step should be self-contained with all necessary context from previous results. \
    The final step should provide the complete answer to the original objective.

    If still need more steps,Generate the next step that:
        1. Builds upon the existing results
        2. Contains all necessary context from previous steps
        3. Is a single, clear and executable task
        4. Moves us closer to the final answer

    If no more steps are needed, respond with the final answer:
        First, summarize all completed steps and their results as a process summary.
        Then, give the final answer result to the user input

    please use Chinese.""" +
    """Current objective:
    {input}

    Original plan:
    {plan}

    Completed steps and their results:
    {past_steps}
    """
)
replanner = replanner_prompt | base_llm.with_structured_output(Act)

async def execute_step(state: PlanExecute):
    task = state["plan"][0]
    task_formatted = f"请执行以下任务:\n{task}"
    output_logger.log(f"开始执行任务: {task}")
    agent_response = await agent_executor.ainvoke(
        {"messages": [("user", task_formatted)]}
    )
    result = agent_response["messages"][-1].content
    output_logger.log(f"任务完成: {task}\n结果: {result}")
    return {"past_steps": [(task, result)]}

async def plan_step(state: PlanExecute):
    output_logger.log(f"开始规划任务: {state['input']}")
    plan = await planner.ainvoke({"messages": [("user", state["input"])]})
    output_logger.log("规划完成:")
    for step in plan.steps:
        output_logger.log(f"- {step}")
    return {"plan": plan.steps}

async def replan_step(state: PlanExecute):
    output_logger.log("重新评估当前进度...")
    output = await replanner.ainvoke(state)
    if isinstance(output.action, Response):
        output_logger.log("生成最终响应")
        return {"response": output.action.response}
    else:
        output_logger.log("生成新的计划:")
        for step in output.action.steps:
            output_logger.log(f"- {step}")
        return {"plan": output.action.steps}

def should_end(state: PlanExecute):
    if "response" in state and state["response"]:
        return END
    else:
        return "agent"

def pretty_print(event):
    if "planner" in event:
        st.session_state["messages"].append({"role": "assistant", "content": "【规划任务步骤】"})
        with st.chat_message("assistant"):
            st.markdown("【规划任务步骤】")
        for idx, step in enumerate(event["planner"]["plan"], 1):
            output_logger.log(f"{step}")
            st.session_state["messages"].append({"role": "assistant", "content": f"{step}"})
            st.markdown(f"{step}")
    if "agent" in event:
        output_logger.log("【执行结果】")
        st.session_state["messages"].append({"role": "assistant", "content": "【执行结果】"})
        with st.chat_message("assistant"):
            st.markdown("【执行结果】")
        for step, result in event["agent"]["past_steps"]:
            output_logger.log(f"步骤: {step}")
            output_logger.log(f"结果: {result}")
            st.session_state["messages"].append({"role": "assistant", "content": f"步骤: {step}\n结果: {result}"})
            with st.chat_message("assistant"):
                st.markdown(f"步骤: {step}\n结果: {result}")
    if "replan" in event:
        if "plan" in event["replan"]:
            output_logger.log("【重新规划任务】")
            st.session_state["messages"].append({"role": "assistant", "content": "【重新规划任务】"})
            with st.chat_message("assistant"):
                st.markdown("【重新规划任务】")
            for idx, step in enumerate(event["replan"]["plan"], 1):
                output_logger.log(f"{step}")    
                st.session_state["messages"].append({"role": "assistant", "content": f"{step}"})
                with st.chat_message("assistant"):
                    st.markdown(f"{step}")  
        if "response" in event["replan"]:
            output_logger.log("【最终结果】")
            st.session_state["messages"].append({"role": "assistant", "content": "【最终结果】"})
            with st.chat_message("assistant"):
                st.markdown("【最终结果】")
            output_logger.log(f"{event['replan']['response']}")
            st.session_state["messages"].append({"role": "assistant", "content": f"【最终结果】\n{event['replan']['response']}"})
            with st.chat_message("assistant"):
                st.markdown(f"【最终结果】\n{event['replan']['response']}")

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
    
    if prompt:
        # 添加用户消息到历史记录
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # 创建状态对象
        state = PlanExecute(
            input=prompt,
            plan=[],
            past_steps=[],
            response=""
        )
        
        # 使用 asyncio 运行异步任务
        async def run_agent_async():
            workflow = StateGraph(PlanExecute)
            workflow.add_node("planner", plan_step)
            workflow.add_node("agent", execute_step)
            workflow.add_node("replan", replan_step)
            workflow.add_edge(START, "planner")
            workflow.add_edge("planner", "agent")
            workflow.add_edge("agent", "replan")
            workflow.add_conditional_edges("replan", should_end, ["agent", END])
            app = workflow.compile()
            
            config = {"recursion_limit": 50}
            inputs = {"input": prompt}
            
            with st.spinner("FengAgent正在思考..."):
                async for event in app.astream(inputs, config=config):
                    pretty_print(event)
        
        # 在 Streamlit 中运行异步代码
        asyncio.run(run_agent_async())

# 添加侧边栏说明
with st.sidebar:
    st.header("使用说明")
    st.markdown("""
    1. 在输入框中输入任务，如“帮我分析新能源领域的股票情况”
    2. FengAgent会分析您的问题并任务规划
    3. 在依次执行子任务的过程中，会基于当前任务结果进行重新规划            
    3. 您可以查看执行过程和最终结果
    4. 所有对话历史都会被保存
    5. 使用"清空内容"按钮可以清空当前页面所有内容
    """) 