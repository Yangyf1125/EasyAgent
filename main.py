import asyncio
import sys
import json
import os
from datetime import datetime
from src.workflow.agent import create_workflow
from langchain_mcp_adapters.client import MultiServerMCPClient
from src.config.logger import output_logger

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
    """检查API key是否有效"""
    config_path = os.path.join('config', 'llm_config.json')
    if not os.path.exists(config_path):
        return False
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
        api_key = config.get('deepseek', {}).get('api_key')
    return api_key.startswith('sk-')

def load_mcp_config():
    """加载MCP配置文件"""
    try:
        with open('config/mcp_config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        output_logger.log(f"加载MCP配置文件失败: {str(e)}")
        return {}

def print_examples():
    """打印示例任务"""
    output_logger.log("\n💡 任务示例：")
    output_logger.log("\n股票分析：")
    output_logger.log("- 请帮我分析近期新能源股票的情况")
    output_logger.log("- 帮我获取比亚迪的涨跌情况")
    output_logger.log("- 分析一下近期的A股市场走势")
    output_logger.log("\n查询搜索：")
    output_logger.log("- 帮我搜索和总结近两年关于大模型的高被引论文")
    output_logger.log("- 目前热门的开源Agent框架有哪些？")

def pretty_print(event):
    """美化输出事件内容"""
    if "planner" in event:
        output_logger.log("【规划任务步骤】")
        for idx, step in enumerate(event["planner"]["plan"], 1):
            output_logger.log(f"{step}")
    
    if "agent" in event:
        output_logger.log("【步骤执行结果】")
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

async def main():
    output_logger.log("🤖 EasyAgent 智能体")
    output_logger.log("EasyAgent是一个基于langchain的Planning Agent，接入了网页搜索、股票查询、arxiv数据库等MCP工具")
    
    # 检查API key
    if not check_api_key():
        output_logger.log("⚠️ 请先在config/llm_config.json中配置您的Deepseek API Key")
        return
    if not if_api_valid():
        output_logger.log("⚠️ 请设置格式正确的Deepseek API Key，例如sk-xxxxxxx")
        return

    # 加载MCP配置
    mcp_config = load_mcp_config()
    if not mcp_config:
        output_logger.log("⚠️ 未找到MCP配置文件，将使用默认配置")
        mcp_config = {
            "mcp-akshare": {
                "command": "uvx",
                "args": ["src/tool/mcp-akshare"],
            },
            "tavily-mcp": {
                "command": "npx",
                "args": ["-y", "tavily-mcp"],
                "env": {"TAVILY_API_KEY": "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"},
                "autoApprove": []
        }
        }
    client = MultiServerMCPClient(mcp_config)
    tools = client.get_tools()
    
    # 获取所有可用的服务名称
    enabled_services = list(mcp_config.keys())
    
    # 打印示例任务
    print_examples()
    
    while True:
        output_logger.log("\n" + "=" * 80)
        user_input = input("\n请输入您的任务（输入exit退出）：")
        
        if user_input.lower() == 'exit':
            #output_logger.log("程序结束")
            break
            
        if not user_input.strip():
            continue
            
        output_logger.log(f"\n正在处理任务：{user_input}")
        
        # 初始化工作流，使用所有可用的服务
        workflow = create_workflow(tools, enabled_services)
        
        # 运行工作流
        config = {"recursion_limit": 50}
        inputs = {"input": user_input}
        
        try:
            async for event in workflow.astream(inputs, config=config):
                pretty_print(event)
        except Exception as e:
            output_logger.log(f"处理任务时出错：{str(e)}")
        
        output_logger.log("\n"+"=" * 80)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        output_logger.log("\n程序被用户中断")
    except Exception as e:
        output_logger.log(f"程序异常终止: {str(e)}")
    finally:
        output_logger.log("程序结束") 