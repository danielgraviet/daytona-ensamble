from agents import martian_client
import pytest

@pytest.mark.asyncio
async def test_client():
    agent = martian_client.MartianAgent()
    code = await agent.generate_code(prompt="Show me a fibonacci sequence code in python.")
    print(code)
    assert code is not None