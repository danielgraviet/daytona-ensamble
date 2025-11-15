import asyncio
from agents.martian_client import MartianAgent
from agents.orchestrator import Orchestrator
from human_eval import human_eval_loader

async def main():
    ds = human_eval_loader._load_human_eval_data()
    problem = ds[1]
    agent = MartianAgent()
    orch = Orchestrator(llm=agent)
    results = await orch.run_problem(problem)
    for r in results:
        print(r)

    await orch.shutdown()

asyncio.run(main())
