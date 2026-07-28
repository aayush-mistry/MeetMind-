import os
import json
from groq import AsyncGroq
from app.services.ai.base_provider import AIService, ProviderError
from app.services.ai.prompts import SYSTEM_EXTRACTION_PROMPT, CHAT_PROMPT_TEMPLATE


class GroqProvider(AIService):
    def __init__(self):
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ProviderError("GROQ_API_KEY is missing from environment variables.")
        try:
            self.client = AsyncGroq(api_key=api_key)
        except Exception as e:
            raise ProviderError(f"Failed to initialize Groq client: {e}")

    async def extract_meeting_intelligence(self, transcript: str) -> dict:
        prompt = SYSTEM_EXTRACTION_PROMPT.format(transcript=transcript)
        try:
            response = await self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
            )
            raw_text = response.choices[0].message.content.strip()

            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            raw_text = raw_text.strip()

            return json.loads(raw_text)
        except Exception as e:
            raise ProviderError(f"Groq API error during extraction: {str(e)}")

    async def transcribe_and_translate(self, file_path: str) -> tuple[str, str]:
        try:
            with open(file_path, "rb") as file:
                response = await self.client.audio.translations.create(
                    file=(os.path.basename(file_path), file.read()),
                    model="whisper-large-v3",
                )
            return "Auto-detected", response.text
        except Exception as e:
            raise ProviderError(f"Groq transcription failed: {str(e)}")

    async def chat(self, context: str, query: str) -> str:
        prompt = CHAT_PROMPT_TEMPLATE.format(context=context, query=query)
        try:
            response = await self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise ProviderError(f"Groq API error during chat: {str(e)}")
