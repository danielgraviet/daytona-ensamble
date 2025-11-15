import datasets as hf_datasets
import pydantic

class _HumanEvalDataPoint(pydantic.BaseModel):
    task_id: str
    prompt: str
    canonical_solution: str
    test: str
    entry_point: str


def _load_human_eval_data() -> list[_HumanEvalDataPoint]:
    ds = hf_datasets.load_dataset("openai/openai_humaneval", split="test")
    results: list[_HumanEvalDataPoint] = []
    for x in ds:
        problem = _HumanEvalDataPoint (
            task_id=x["task_id"],
            prompt=x["prompt"],
            canonical_solution=x["canonical_solution"],
            test=x["test"],
            entry_point=x["entry_point"],
        )
        results.append(problem)
    return results