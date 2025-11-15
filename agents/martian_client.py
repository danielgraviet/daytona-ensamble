from __future__ import annotations
import openai


class MartianAgent:
    """Thin wrapper around the Martian OpenAI-compatible API for code generation."""

    def __init__(self):
        base_url = "https://api.withmartian.com/v1"
        
        self.client = openai.AsyncOpenAI(
            base_url=base_url,
        )

    async def generate_code(self, prompt: str, model: str = "openai/gpt-4.1-nano") -> str:
        """Generate code for a given problem prompt using Martian API."""
        response = await self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )

        # Return model-generated text
        return response.choices[0].message.content
