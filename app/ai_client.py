import asyncio


class MockAIError(Exception):
    pass


class MockAIClient:
    def __init__(self, delay_seconds: int = 2) -> None:
        self.delay_seconds = delay_seconds

    async def generate_answer(self, message: str) -> str:
        await asyncio.sleep(self.delay_seconds)
        if "[fail-ai]" in message.lower():
            raise MockAIError("Mock AI failure requested")
        return "Generated Answer."

