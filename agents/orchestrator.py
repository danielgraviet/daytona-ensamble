import asyncio

from agents.martian_client import MartianAgent
from agents.variants import VARIANTS
from utils import utils
from human_eval import human_eval_loader
from models.types import RunResult
from tqdm.asyncio import tqdm_asyncio


class Orchestrator:
    def __init__(self, llm: MartianAgent):
        self.llm = llm

    async def _generate_all(self, problem: human_eval_loader._HumanEvalDataPoint) -> list[str]:
        tasks = []

        for variant in VARIANTS:
            prompt = utils.format_prompt_for_agent(problem, variant)
            task = self.llm.generate_code(prompt)
            tasks.append(task)

        # LLM parallel execution
        results = await tqdm_asyncio.gather(*tasks)
        return results
    
    