# EasyAgent

[English](README.md) | [简体中文](README_ZH.md)

EasyAgent 是一个基于 LangChain 和 LangGraph 构建的智能代理系统，它集成了多个MCP工具和服务，能够帮助用户完成各种任务。

## 功能特点

- 🤖 基于 LangChain 和 LangGraph 的智能工作流
- 🔧 集成多个实用MCP工具如：
  - 高德地图服务
  - Tavily 搜索服务
  - AKShare 金融数据服务
- 📊 支持金融数据分析
- 🗺️ 支持地理位置服务
- 🔍 支持智能搜索
- 📝 详细的执行日志记录

## 系统要求

- Python 3.12
- Node.js (可选，用于运行某些 MCP 服务)

## 安装步骤

1. 克隆项目到本地：
```bash
git clone https://github.com/yourusername/EasyAgent.git
cd EasyAgent
```

2. 安装 Python 依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

EasyAgent 提供两种使用方式：命令行界面和 Web 界面。

### 1. 命令行界面

1. 启动主程序：
```bash
python main.py
```

2. 在命令行中输入你想要执行的任务，例如：
   - "请帮我分析新能源领域的股票"
   - "查询北京到上海的路线"

3. 系统会自动调用相应的工具和服务来完成任务

4. 输入 "exit" 可以退出程序

### 2. Web 界面

1. 启动 Web 服务：
```bash
streamlit run app.py
```

2. 在浏览器中打开终端显示的地址（例如 http://localhost:8501）

3. 在 Web 界面中输入任务，系统会自动处理并显示结果

4. Web 界面提供了更友好的交互体验和可视化展示

## 项目结构

```
EasyAgent/
├── src/                # 源代码目录
├── web_app/           # Web 应用相关文件
├── pages/             # 页面文件
├── main.py            # 命令行界面入口
├── app.py             # Web 界面入口
├── requirements.txt   # Python 依赖
└── README.md         # 项目说明文档
```

## 注意事项

- 使用前请确保已正确配置所有必要的 API 密钥
- 部分功能需要网络连接
- 建议在虚拟环境中运行项目

## 许可证

本项目采用 MIT 许可证。查看 [LICENSE](LICENSE) 文件了解更多详情。

## 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进项目。

## 联系方式

yangyf1125@gmail.com

