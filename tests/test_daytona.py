from sandbox import sandbox_runner

_MOCK_PAYLOAD = """
def add(a, b):
    return a + b

assert add(2, 4) == 6
"""

def test_mock_solution():
    code_runner = sandbox_runner.DaytonaSandboxRunner()
    result = code_runner.run_solution(
        payload=_MOCK_PAYLOAD,
        variant_name="baseline"
    )
    print(result)