from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic

# Agente mínimo para pruebas
def get_simple_model():
    return ChatAnthropic(model_name="claude-3-5-haiku-20241022", max_tokens=1000)

agent = create_react_agent(get_simple_model(), [])