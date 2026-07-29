import os
import json
import asyncio
from starlette.concurrency import run_in_threadpool
from app.services.ai.base_provider import AIService, ProviderError
from app.services.ai.prompts import (
    SYSTEM_EXTRACTION_PROMPT,
    AUDIO_TRANSCRIPTION_PROMPT,
    CHAT_PROMPT_TEMPLATE,
)


class GeminiProvider(AIService):
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ProviderError("GEMINI_API_KEY is missing from environment variables.")
        try:
            from google import genai

            self.client = genai.Client(api_key=api_key)
        except ImportError:
            raise ProviderError("google-genai SDK is not installed.")

    async def extract_meeting_intelligence(self, transcript: str) -> dict:
        prompt = SYSTEM_EXTRACTION_PROMPT.format(transcript=transcript)
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=prompt,
                ),
            )
            raw_text = response.text.strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            raw_text = raw_text.strip()

            return json.loads(raw_text)
        except Exception as e:
            raise ProviderError(f"Gemini API error during extraction: {str(e)}")

    async def transcribe_and_translate(self, file_path: str) -> tuple[str, str]:
        try:
            uploaded_file = await run_in_threadpool(
                self.client.files.upload, file=file_path
            )

            response = await run_in_threadpool(
                self.client.models.generate_content,
                model="gemini-1.5-flash",
                contents=[AUDIO_TRANSCRIPTION_PROMPT, uploaded_file],
            )

            await run_in_threadpool(self.client.files.delete, name=uploaded_file.name)

            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            data = json.loads(text.strip())

            detected_lang = data.get("original_language", "Unknown")
            transcript = data.get("english_transcript", "")
            original_transcript = data.get("original_transcript", transcript)
            return detected_lang, transcript, original_transcript

        except Exception as e:
            raise ProviderError(f"Gemini transcription failed: {str(e)}")

    async def chat(self, context: str, query: str) -> str:
        prompt = CHAT_PROMPT_TEMPLATE.format(context=context, query=query)
        try:
            response = await run_in_threadpool(
                self.client.models.generate_content,
                model="gemini-1.5-flash",
                contents=prompt,
            )
            return response.text
        except Exception as e:
            raise ProviderError(f"Gemini API error during chat: {str(e)}")
