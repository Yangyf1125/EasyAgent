from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, START, END
from src.config.logger import output_logger
from src.models.llm import get_llm, get_prompt, get_planner_prompt, get_replanner_prompt
from src.types.models import PlanExecute, Plan, Act, Response
import traceback

class WorkflowManager:
    def __init__(self):
        self.agent_executor = None
        self.planner = None
        self.replanner = None

    async def execute_step(self, state: PlanExecute):
        if not self.agent_executor:
            raise RuntimeError("Agent executor not initialized")
            
        past=state["past_steps"]
        past_formatted  = f"已经完成的任务：\n{past}\n"
        task = state["plan"][0]
        task_formatted = past_formatted + f"请执行以下任务:\n{task}"
        output_logger.log("")
        #output_logger.log(f"目前完成的任务：{past_formatted}")
        output_logger.log(f"【开始执行任务】: {task}")
        agent_response = await self.agent_executor.ainvoke(
            {"messages": [("user", task_formatted)]}
        )
        result = agent_response["messages"][-1].content
        #output_logger.log(f"【任务完成】: {task}\n结果: {result}")
        output_logger.log(f"【任务完成】")
        return {"past_steps": [(task, result)]}

    async def plan_step(self, state: PlanExecute):
        if not self.planner:
            raise RuntimeError("Planner not initialized")
        output_logger.log(f"")
        output_logger.log(f"【开始规划任务】: {state['input']}\n")
        plan = await self.planner.ainvoke({"messages": [("user", state["input"])]})
        #output_logger.log("规划完成:")
        #for step in plan.steps:
            #output_logger.log(f"- {step}")
        return {"plan": plan.steps}

    async def replan_step(self, state: PlanExecute):
        if not self.replanner:
            raise RuntimeError("Replanner not initialized")
        output_logger.log("")
        output_logger.log("【重新评估当前进度】...")
        output = await self.replanner.ainvoke(state)
        if isinstance(output.action, Response):
            output_logger.log("生成最终响应")
            return {"response": output.action.response}
        else:
            output_logger.log("【生成新的计划】:")
            for step in output.action.steps:
                output_logger.log(f"    - {step}")
            return {"plan": output.action.steps}

    def should_end(self, state: PlanExecute):
        if "response" in state and state["response"]:
            return END
        else:
            return "agent"

    def pretty_print(self, event):
        if not event:
            output_logger.log("【警告】事件为空")
            return
            
        if "planner" in event:
            output_logger.log("【规划任务步骤】")
            for idx, step in enumerate(event["planner"]["plan"], 1):
                output_logger.log(f"{step}")
        if "agent" in event:
            output_logger.log("【执行结果】")
            for step, result in event["agent"]["past_steps"]:
                output_logger.log(f"    步骤: {step}")
                output_logger.log(f"    结果: {result}")
        if "replan" in event:
            if "plan" in event["replan"]:
                output_logger.log("【重新规划任务】")
                for idx, step in enumerate(event["replan"]["plan"], 1):
                    output_logger.log(f"    {step}")
            if "response" in event["replan"]:
                output_logger.log("【最终结果】")
                output_logger.log(f"{event['replan']['response']}")

    def create_workflow(self, tools, enabled_services):
        try:
            output_logger.log("正在初始化Agent执行器...")
            prompt = get_prompt(enabled_services)
            llm = get_llm()
            self.agent_executor = create_react_agent(llm, tools, prompt=prompt)
            
            output_logger.log("正在初始化规划器...")
            self.planner = get_planner_prompt() | llm.with_structured_output(Plan)
            
            output_logger.log("正在初始化重规划器...")
            self.replanner = get_replanner_prompt() | llm.with_structured_output(Act)

            output_logger.log("正在创建工作流图...")
            workflow = StateGraph(PlanExecute)
            
            # 绑定实例方法到工作流节点
            workflow.add_node("planner", self.plan_step)
            workflow.add_node("agent", self.execute_step)
            workflow.add_node("replan", self.replan_step)
            
            # 添加边
            workflow.add_edge(START, "planner")
            workflow.add_edge("planner", "agent")
            workflow.add_edge("agent", "replan")
            workflow.add_conditional_edges("replan", self.should_end, ["agent", END])
            
            output_logger.log("工作流创建完成")
            return workflow.compile()
            
        except Exception as e:
            error_msg = f"创建工作流时出错: {str(e)}\n{traceback.format_exc()}"
            output_logger.log(error_msg)
            raise

# 创建全局工作流管理器实例
workflow_manager = WorkflowManager()

# 导出函数
create_workflow = workflow_manager.create_workflow
pretty_print = workflow_manager.pretty_print 