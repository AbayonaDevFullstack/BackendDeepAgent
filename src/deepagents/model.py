from langchain_anthropic import ChatAnthropic


def get_default_model():
    return ChatAnthropic(
        model_name="claude-3-5-haiku-20241022",
        max_tokens=8192,   # Máximo permitido para Haiku
        temperature=0.3,   # Más creatividad para explicaciones detalladas
        top_p=0.9         # Permite variedad en explicaciones
    )
