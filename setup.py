"""
Setup script para instalar deepagents como paquete local en Render
"""
from setuptools import setup, find_packages

setup(
    name="deepagents",
    version="1.0.0",
    description="Deep Agent framework for LangGraph",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "langgraph>=0.6.6",
        "langchain>=0.3.27",
        "langchain-anthropic>=0.3.19",
        "langchain-core>=0.3.75",
        "langsmith>=0.4.21",
        "pydantic>=2.11.7",
        "httpx>=0.28.1",
        "fastapi>=0.104.0",
        "uvicorn>=0.35.0",
    ],
)