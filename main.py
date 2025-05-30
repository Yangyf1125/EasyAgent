import asyncio
import sys
import signal
import threading
import traceback
from langchain_mcp_adapters.client import MultiServerMCPClient
from src.config.logger import output_logger
from src.workflow.agent import create_workflow, pretty_print

# 设置 Windows 上的事件循环策略
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

def handle_interrupt(signum, frame):
    """处理中断信号"""
    output_logger.log(f"收到中断信号 {signum}, 正在终止程序...")
    raise KeyboardInterrupt

async def cleanup(client):
    """清理资源"""
    try:
        output_logger.log("MCP连接已关闭")
    except Exception as e:
        output_logger.log(f"关闭连接时出错: {str(e)}")

async def main():
    # 只在主线程中注册信号处理
    # if threading.current_thread() is threading.main_thread():
    #     signal.signal(signal.SIGINT, handle_interrupt)
    #     signal.signal(signal.SIGTERM, handle_interrupt)
    
    client = None
    try:
        output_logger.log("正在初始化MCP客户端...")
        client = MultiServerMCPClient(
            {
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
                    "url": "https://mcp.api-inference.modelscope.cn/sse/bf53f78667f54f",
                    "transport": "sse",
                    },
                "akshare-one-mcp": {
                    "type": "sse",
                    "url": "https://mcp.api-inference.modelscope.cn/sse/2546d617f8e445",
                    "transport": "sse",
                    },

                "mcp-yahoo-finance": {
                    "type": "sse",
                    "url": "https://mcp.api-inference.modelscope.cn/sse/44b98b6a7e8046",
                    "transport": "sse",
                    },
                "fetch": {
                    "type": "sse",
                    "url": "https://mcp.api-inference.modelscope.cn/sse/5c537afd52804f",
                    "transport": "sse",
                    },

                "arxiv-mcp-server": {
                    "type": "sse",
                    "url": "https://mcp.api-inference.modelscope.cn/sse/5da5bf0f0c604d",
                    "transport": "sse",
                    },
                "mcp-server-chart": {
                    "type": "sse",
                    "url": "https://mcp.api-inference.modelscope.cn/sse/2b2af34ca5794a",
                    "transport": "sse",
                    },
                "time-mcp": {
                    "type": "sse",
                    "url": "https://mcp.api-inference.modelscope.cn/sse/5bd40c9faeea44",
                    "transport": "sse",
                    }
            }
        )
        
        async with client:
            output_logger.log("MCP客户端初始化完成")
            output_logger.log("正在获取工具...")
            tools = client.get_tools()
            import os
            # from langchain_tavily import TavilySearch
            # os.environ["TAVILY_API_KEY"]="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"
            # tools +=[TavilySearch(max_results=5,topic="general")]
            output_logger.log(f"成功获取 {len(tools)} 个工具")
            
            output_logger.log("正在创建工作流...")
            app = create_workflow(tools)
            output_logger.log("准备接收用户输入")

            while True:
                output_logger.log("\n" + "#" * 80)
                config = {"recursion_limit": 50}
                user_input = input("输入任务(输入exit退出)，如“请帮我分析新能源领域的股票”\n您的任务： ")
                if user_input == "exit":
                    output_logger.log("程序结束")
                    break
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