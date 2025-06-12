# EasyAgent

[English](README.md) | [简体中文](README_ZH.md)

EasyAgent is a beginner-friendly intelligent agent system built on LangChain and LangGraph, integrating various practical MCP tools and services to help users complete various basic tasks.

## ✨ Main Features

- 🤖 Intelligent workflow based on LangChain and LangGraph
- 🔧 Integration of multiple MCP tools and services:
  - Web search service
  - AKShare A-share data
  - Yahoo Finance financial data
  - ArXiv research paper library
  - Amap geographic service
- 📊 Financial data analysis support
- 🔍 Intelligent search capabilities
- 🎨 Simple and intuitive web interface

## 🚀 System Requirements

- Python 3.12
- Node.js (optional, for running certain MCP services)

## 📦 Installation Steps

1. Clone the repository:
```bash
git clone https://github.com/Yangyf1125/EasyAgent.git
cd EasyAgent
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

#### 1. LLM Configuration
Configure LLM settings in the 🐋Deepseek page of the web interface or in `config/llm_config.json`. Currently only Deepseek is supported:
  - `api_key`: Your Deepseek API key

#### 2. MCP Configuration
Configure various MCP tools and services in `config/mcp_config.json`:
```json
{
  "server1": {
    "type": "sse",
    "url": "http://localhost:8000/sse"
  }
}
    // Other MCP service configurations...
```
Currently using Modelscope's remote MCP server, please modify as needed

## 💻 Usage
Provides both terminal and web interfaces.

#### Terminal

Start the terminal interface:
```bash
python main.py
```

#### Web UI
Provides a simple web interface that can be deployed locally or accessed directly through the [web service](https://easyagentyyf.streamlit.app) deployed on Streamlit Cloud.

1. Start the web service:
```bash
streamlit run Homepage.py
```

2. Access the web interface at  the URL provided in your terminal(e.g.,`http://localhost:8501`)

## 📁 Project Structure

```
EasyAgent/
├── src/                # Source code directory
│   ├── config/        # Configuration files
│   ├── workflow/      # Workflow related code
│   └── tool/          # Tool implementations
├── pages/             # Web page files
├── config/            # Configuration directory
├── main.py            # CLI entry point
├── Homepage.py        # Web interface entry point
├── requirements.txt   # Python dependencies
└── README.md         # Project documentation
```

## ⚠️ Notes

- Please ensure all necessary API keys are properly configured before use
- Some features require internet connection
- It is recommended to run the project in a virtual environment
- Make sure all necessary dependencies are installed

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Issues and Pull Requests are welcome to help improve the project.

## 📧 Contact

u3621301@connect.hku.hk
yangyf1125@gmail.com 