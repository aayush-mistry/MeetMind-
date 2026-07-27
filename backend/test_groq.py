import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
from app.services.ai.provider_factory import get_ai_provider

async def test():
    provider = get_ai_provider()
    print("Using provider:", type(provider).__name__)
    res = await provider.extract_meeting_intelligence("Alice: Let's migrate to AWS. Bob: Agreed. Bob will do it by tomorrow.")
    print(res)

if __name__ == "__main__":
    asyncio.run(test())
