# EasyAgent

[English](README.md) | [简体中文](README_ZH.md)

EasyAgent is an intelligent agent system built on LangChain and LangGraph, integrating practical MCP tools and services to help users accomplish various basic tasks.

## Features

- 🤖 Intelligent workflow based on LangChain and LangGraph
- 🔧 Integration of multiple MCP tools such as:
  - Tavily search service
  - AKShare financial data service
  - ArXiv's research repository
  - Amap service
- 📊 Financial data analysis support
- 🗺️ Location-based services
- 🔍 Intelligent search capabilities
- 📝 Detailed execution logging
- 🎨 Simple and intuitive web interface

## System Requirements

- Python 3.12
- Node.js (optional, for running certain MCP services)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Yangyf1125/EasyAgent.git
cd EasyAgent
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

EasyAgent provides two ways to use: Command Line Interface (CLI) and Web Interface.

### 1. Command Line Interface

1. Start the main program:
```bash
python main.py
```

2. Enter your task in the command line, for example:
   - "Please analyze stocks in the new energy sector"
   - "Find the route from Beijing to Shanghai"

3. The system will automatically call the appropriate tools and services to complete the task

4. Type "exit" to quit the program

### 2. Web Interface

1. Start the web service:
```bash
streamlit run Homepage.py
```

2. Open the address shown in the terminal (typically http://localhost:8501)

3. Enter your task in the web interface, and the system will process and display the results

4. The web interface provides a more user-friendly experience with visual presentations

## Project Structure

```
EasyAgent/
├── src/                # Source code directory
├── web_app/           # Web application files
├── pages/             # Page files
├── main.py            # CLI entry point
├── app.py             # Web interface entry point
├── requirements.txt   # Python dependencies
└── README.md         # Project documentation
```

## Notes

- Make sure all necessary API keys are properly configured before use
- Some features require internet connection
- It's recommended to run the project in a virtual environment

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Issues and Pull Requests are welcome to help improve the project.

## Contact

yangyf1125@gmail.com 