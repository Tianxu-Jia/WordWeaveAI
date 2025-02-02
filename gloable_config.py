from crewai import LLM
import os

llm_ollama = LLM(
    model="ollama/phi4:latest",
    base_url="http://localhost:11434"
)

llm_deepseek = LLM(
    model="deepseek/deepseek-chat",
    api_key=os.environ["DEEPSEEK_API_KEY"],
    temperature=1.5
)