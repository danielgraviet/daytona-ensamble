from agents import orchestrator, martian_client
from human_eval.human_eval_loader import _HumanEvalDataPoint
import pytest


MOCK_PROBLEM = _HumanEvalDataPoint(
    task_id="HumanEval/0",
    prompt=(
        "from typing import List\n\n"
        "def has_close_elements(numbers: List[float], threshold: float) -> bool:\n"
        '    """ Check if in given list of numbers, are any two numbers closer to each other than\n'
        "    given threshold.\n"
        "    >>> has_close_elements([1.0, 2.0, 3.0], 0.5)\n"
        "    False\n"
        "    >>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)\n"
        "    True\n"
        '    """\n'
    ),
    canonical_solution=(
        "    for idx, elem in enumerate(numbers):\n"
        "        for idx2, elem2 in enumerate(numbers):\n"
        "            if idx != idx2:\n"
        "                distance = abs(elem - elem2)\n"
        "                if distance < threshold:\n"
        "                    return True\n\n"
        "    return False\n"
    ),
    test=(
        "\n\nMETADATA = {\n"
        "    'author': 'jt',\n"
        "    'dataset': 'test'\n"
        "}\n\n"
        "def check(candidate):\n"
        "    assert candidate([1.0, 2.0, 3.9, 4.0, 5.0, 2.2], 0.3) == True\n"
        "    assert candidate([1.0, 2.0, 3.9, 4.0, 5.0, 2.2], 0.05) == False\n"
        "    assert candidate([1.0, 2.0, 5.9, 4.0, 5.0], 0.95) == True\n"
        "    assert candidate([1.0, 2.0, 5.9, 4.0, 5.0], 0.8) == False\n"
        "    assert candidate([1.0, 2.0, 3.0, 4.0, 5.0, 2.0], 0.1) == True\n"
        "    assert candidate([1.1, 2.2, 3.1, 4.1, 5.1], 1.0) == True\n"
        "    assert candidate([1.1, 2.2, 3.1, 4.1, 5.1], 0.5) == False\n\n"
    ),
    entry_point="has_close_elements",
)


@pytest.mark.asyncio
async def test_inference_only_generate_all():
    agent = martian_client.MartianAgent()


    orc = orchestrator.Orchestrator(
        llm=agent,
    )

    results = await orc._generate_all(problem=MOCK_PROBLEM)

    # Expect one result per variant
    assert len(results) == 5

    # Print results for inspection
    print("\n====== LLM RAW OUTPUTS ======")
    for idx, r in enumerate(results, start=1):
        print(f"\n--- Variant {idx} ---\n")
        print(r[:500])  # print just the first 500 chars

    # Basic sanity: results should not be empty
    for r in results:
        assert isinstance(r, str)
        assert len(r.strip()) > 0