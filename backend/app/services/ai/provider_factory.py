import os
from app.services.ai.base_provider import AIService

def get_ai_provider() -> AIService:
    """
    Factory function to instantiate the correct AI provider based on AI_PROVIDER env var.
    """
    provider_name = os.environ.get("AI_PROVIDER", "gemini").lower().strip()
    
    if provider_name == "groq":
        from app.services.ai.groq_provider import GroqProvider
        return GroqProvider()
    elif provider_name == "openai":
        from app.services.ai.openai_provider import OpenAIProvider
        return OpenAIProvider()
    elif provider_name == "openrouter":
        from app.services.ai.openrouter_provider import OpenRouterProvider
        return OpenRouterProvider()
    else:
        # Default fallback to Gemini for backward compatibility
        from app.services.ai.gemini_provider import GeminiProvider
        return GeminiProvider()
