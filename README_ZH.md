# EasyAgent

[English](README.md) | [简体中文](README_ZH.md)

EasyAgent 是一个基于 LangChain 和 LangGraph 构建的入门级智能代理系统，集成了多种实用的 MCP 工具和服务，帮助用户完成各种基础任务。

## ✨ 主要特性

- 🤖 基于 LangChain 和 LangGraph 的智能工作流
- 🔧 集成多种 MCP 工具和服务：
  - 网络搜索服务
  - AKShare A股数据
  - Yahoo Finance 雅虎财经数据
  - ArXiv 研究论文库
  - 高德地理服务

- 📊 金融数据分析支持
- 🔍 智能搜索能力
- 🎨 简洁直观的 Web 界面

## 🚀 系统要求

- Python 3.12
- Node.js（可选，可能会用于运行某些 MCP 服务）

## 📦 安装步骤

1. 克隆仓库：
```bash
git clone https://github.com/Yangyf1125/EasyAgent.git
cd EasyAgent
```

2. 安装 Python 依赖：
```bash
pip install -r requirements.txt
```
## ⚙️ Configuration

#### 1.LLM Configuration
在网页端中的🐋Deepseek页面或 `config/llm_config.json` 中配置LLM相关设置,目前暂时仅支持Deepseek：
  - `api_key`: 您的Deepseek API密钥

#### 2.MCP Configuration
在 `config/mcp_config.json` 中配置各种MCP工具和服务：
```json
{
  "server1": {
    "type": "sse",
    "url": "http://localhost:8000/sse"
  }
}
    // 其他MCP服务配置...
```
目前使用的是Modelscope的远程MCP服务器，如有需要请自行修改

## 💻 使用方法
提供命令行和 Web 两种使用方式。
#### 命令行

启动命令行入口：
```bash
python main.py
```



#### Web UI
提供一个简易的 Web 界面，可在本地部署或是直接访问部署到streamlit cloud的[网页端服务](https://easyagentyyf.streamlit.app)

1. 启动 Web 服务：
```bash
streamlit run Homepage.py
```

2. 打开终端显示的地址（例如 http://localhost:8501）


## 📁 项目结构

```
EasyAgent/
├── src/                # 源代码目录
│   ├── config/        # 配置文件
│   ├── workflow/      # 工作流相关代码
│   └── tool/          # 工具实现
├── pages/             # Web 页面文件
├── config/            # 配置文件目录
├── main.py            # CLI 入口点
├── Homepage.py        # Web 界面入口点
├── requirements.txt   # Python 依赖
└── README.md         # 项目文档
```

## ⚠️ 注意事项

- 使用前请确保所有必要的 API 密钥已正确配置
- 部分功能需要互联网连接
- 建议在虚拟环境中运行项目
- 确保系统已安装所有必要的依赖

## 📄 许可证

本项目采用 MIT 许可证。详情请参见 [LICENSE](LICENSE) 文件。

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进项目。

## 📧 联系方式

u3621301@connect.hku.hk
yangyf1125@gmail.com


