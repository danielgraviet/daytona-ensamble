<div align="center">
  <img src="assets/code_quintet_logo.png" alt="Code Quintet Logo" width="220">
  <h1>Code Quintet – Daytona Code Ensemble </h1>
  <p>Five coordinated LLM voices tackling different coding problems.</p>
</div>

Generate multiple LLM-written solutions for a coding task, execute each one in an isolated Daytona sandbox, and instantly compare correctness, runtime, and other qualities. Powered by Daytona sandboxes, HumanEval, and a curated set of prompt variants.

---

## Highlights

- **🔄 Ensemble generation** – five prompt variants (baseline, no-external-libs, memory-efficient, performance, super-readable) per task.
- **🧪 Real HumanEval tests** – every candidate runs against the official prompt + hidden tests for the task ID.
- **🔐 Isolated execution** – Daytona sandboxes prevent one variant from impacting others.
- **🧭 Human-in-the-loop selection** – focus on correctness, speed, memory, or readability when reviewing the run.
- **📊 Rich CLI output** – runtime, pass/fail info, stdout/stderr, and failure traces.
- **📁 Saved artifacts** – every run is persisted to `results/run_<id>` for later inspection or training.
- **🛒 Variant Marketplace** – plug-and-play solution “styles” you can enable, disable, or swap instantly to customize your ensemble.
- **📈 Monitoring Dashboard** – a lightweight live dashboard to track runs, model performance, and sandbox activity in real time.
---

## How It Works

1. Launch the CLI and choose a HumanEval task (`HumanEval/0…164`) or ask for a random one.
2. The orchestrator formats the problem for each variant and prompts the configured LLM.
3. Generated code is extracted, bundled with the task’s tests, and executed inside Daytona sandboxes.
4. Results (pass/fail, runtime, stdout/stderr) are aggregated and printed with the fastest passing variant highlighted.
5. If desired, review the exact source for any variant directly inside the CLI.

```
=== Summary ===
Variant             Passed  Runtime(ms)  Error
------------------------------------------------
baseline            10/10   4.3          -
performance         10/10   2.1          -
memory_efficient    10/10   3.0          -
no_external_libs    9/10    4.8          AssertionError
super_readable      10/10   6.5          -

Goal: speed → Recommended: performance
```

---

## Architecture

```
project/
├── main.py                # CLI entrypoint + Rich UI
├── agents/
│   ├── orchestrator.py    # variant orchestration and sandbox fan-out
│   ├── martian_client.py  # LLM API wrapper
│   └── variants.py        # Variant prompt definitions
├── human_eval/            # HumanEval loader + data
├── sandbox/               # Daytona sandbox runner
├── models/                # Typed dataclasses
├── tests/                 # Local regression tests
└── results/               # Run artifacts (created at runtime)
```

---

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Configure credentials:

```bash
export DAYTONA_API_KEY="your_daytona_key"
export OPENAI_API_KEY="your_llm_key"      # or MARTIAN_API_KEY for the Martian agent
```

---

## Usage

### Run interactively (recommended)

```bash
python main.py
```

You will be prompted to pick an LLM model, select a HumanEval task ID (or `random`), and optionally view the generated source for the fastest passing variant.


## Run Artifacts

Each run produces `results/run_<id>/<variant>/` containing:

- `prompt.txt` – formatted prompt for the variant
- `response.txt` – raw LLM response
- `solution.py` – extracted candidate code
- `payload.py` – code + tests fed to the sandbox
- `result.json` – pass/fail, runtime, stdout/stderr, and metadata

Perfect for qualitative review, regression debugging, or future fine-tuning datasets.

---

## Variant Marketplace (Community Prompts)

Drop JSON manifests into `variants_marketplace/` to register custom prompt variants without touching the codebase. Example:

```json
{
  "name": "my_speedster",
  "description": "Focus on constant-factor performance tricks. Return only the function in ```python``` fences."
}
```

Every manifest must include a unique `name` and `description`. The CLI automatically loads all `*.json` files in that folder and treats them just like the built-in variants, so you can share, rank, or disable them at will.

---

## Limitations

- Memory scoring is a heuristic derived from the variant prompt rather than real measurements.
- No iterative self-correction loop yet; each variant is a single-shot attempt.
- Readability scoring is subjective and based on the “super readable” prompt style.

---

## Roadmap

1. Editor integrations (Cursor / VS Code) for one-click ensemble runs.
2. Train a selector to rank variants without rerunning tests.
3. Automatic refinement when all variants fail. 
4. Multi-model ensembles (reasoning + speed specialists).

---

## ❤️ Credits

Built for the **Daytona 2 Hackathon** using Daytona Sandboxes, HumanEval, Python, and LLM orchestration. PRs and ideas welcome!
