from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple


class ProviderError(Exception):
    """Base exception for all AI provider errors."""

    pass


class RateLimitError(ProviderError):
    """Exception raised when API rate limits are exceeded."""

    pass


class AIService(ABC):
    """Abstract base class for AI providers."""

    @abstractmethod
    async def extract_meeting_intelligence(self, transcript: str) -> Dict[str, Any]:
        """
        Analyze a transcript and extract summary, action items, decisions, and risks.
        Must return a dictionary matching the schema in prompts.py.
        """
        pass

    @abstractmethod
    async def transcribe_and_translate(self, file_path: str) -> tuple[str, str, str]:
        """
        Transcribes audio and translates to English if necessary.
        Returns: (detected_language, english_transcript, original_transcript)
        """
        pass

    @abstractmethod
    async def chat(self, context: str, query: str) -> str:
        """
        Answer a user query based on the provided meeting transcripts context.
        """
        pass
