from setuptools import setup, find_packages

setup(
    name="fengagent",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "langchain",
        "langchain-deepseek",
        "langgraph",
        "langchain-mcp-adapters",
        "pydantic",
        "typing-extensions"
    ]
) 