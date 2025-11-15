from human_eval import human_eval_loader
from sandbox import sandbox_runner
import utils

def test_single_canonical_solution():
    runner = sandbox_runner.DaytonaSandboxRunner()
    ds = human_eval_loader._load_human_eval_data()
    sample = ds[0]
    
    utils.format_payload()