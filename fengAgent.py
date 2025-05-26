import getpass, os, operator, signal, logging
from datetime import datetime
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain_openai.chat_models.base import BaseChatOpenAI
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field
from typing import Annotated, List, Tuple
from typing_extensions import TypedDict
from langchain_core.prompts import ChatPromptTemplate
from typing import Union, Literal
from langgraph.graph import END
from langgraph.graph import StateGraph, START
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio
import threading
import traceback
import sys
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

llm = ChatDeepSeek(model="deepseek-chat", api_key="sk-2574248e129a44cbbb543c8ffcceeec8")
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

async def cleanup(client):
    """清理资源"""
    try:
        #output_logger.log("正在关闭MCP连接...")
        #await client.close()
        output_logger.log("MCP连接已关闭")
    except Exception as e:
        output_logger.log(f"关闭连接时出错: {str(e)}")

def handle_interrupt(signum, frame):
    """处理中断信号"""
    output_logger.log(f"收到中断信号 {signum}, 正在终止程序...")
    raise KeyboardInterrupt

async def main():
    # 只在主线程中注册信号处理
    if threading.current_thread() is threading.main_thread():
        signal.signal(signal.SIGINT, handle_interrupt)
        signal.signal(signal.SIGTERM, handle_interrupt)
    
    client = None
    try:
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
                    "args": ["tool/mcp-akshare"]
                },
            }
        )
        output_logger.log("MCP客户端初始化完成")
        
        async with client:
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
                    output_logger.log("【规划任务步骤】")
                    for idx, step in enumerate(event["planner"]["plan"], 1):
                        output_logger.log(f"{step}")
                if "agent" in event:
                    output_logger.log("【执行结果】")
                    for step, result in event["agent"]["past_steps"]:
                        output_logger.log(f"步骤: {step}")
                        output_logger.log(f"结果: {result}")
                if "replan" in event:
                    if "plan" in event["replan"]:
                        output_logger.log("【重新规划任务】")
                        for idx, step in enumerate(event["replan"]["plan"], 1):
                            output_logger.log(f"{step}")
                    if "response" in event["replan"]:
                        output_logger.log("【最终结果】")
                        output_logger.log(f"{event['replan']['response']}")

            workflow = StateGraph(PlanExecute)
            workflow.add_node("planner", plan_step)
            workflow.add_node("agent", execute_step)
            workflow.add_node("replan", replan_step)
            workflow.add_edge(START, "planner")
            workflow.add_edge("planner", "agent")
            workflow.add_edge("agent", "replan")
            workflow.add_conditional_edges("replan", should_end, ["agent", END])
            app = workflow.compile()

            while True:
                output_logger.log("\n" + "#" * 80)
                config = {"recursion_limit": 50}
                user_input = input("输入任务： (输入exit退出)")
                if user_input == "exit":
                    output_logger.log("程序结束")
                    break
                #output_logger.log(f"用户输入: {user_input}")
                inputs = {"input": user_input}
                async for event in app.astream(inputs, config=config):
                    pretty_print(event)
                output_logger.log("#" * 80)

    except Exception as e:
        error_msg = f"程序发生异常: {str(e)}\n{traceback.format_exc()}"
        output_logger.log(error_msg)
        raise
    finally:
        if client:
            await cleanup(client)

if __name__ == "__main__":
    try:
        output_logger.log("程序启动")
        asyncio.run(main())
    except KeyboardInterrupt:
        output_logger.log("程序被用户中断")
    except Exception as e:
        error_msg = f"程序异常终止: {str(e)}\n{traceback.format_exc()}"
        output_logger.log(error_msg)
        raise
    finally:
        output_logger.log("程序结束")
