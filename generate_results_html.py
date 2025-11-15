from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any, Dict, List


def load_runs(results_dir: Path) -> List[Dict[str, Any]]:
    runs = []
    if not results_dir.exists():
        return runs

    for run_path in sorted(results_dir.glob("run_*")):
        if not run_path.is_dir():
            continue

        variants = []
        for variant_dir in sorted(run_path.iterdir()):
            if not variant_dir.is_dir():
                continue

            result_file = variant_dir / "result.json"
            if not result_file.exists():
                continue

            try:
                result_data = json.loads(result_file.read_text())
            except json.JSONDecodeError:
                continue

            solution = ""
            solution_file = variant_dir / "solution.py"
            if solution_file.exists():
                solution = solution_file.read_text()

            variants.append(
                {
                    "name": variant_dir.name,
                    "result": result_data,
                    "solution": solution,
                }
            )

        runs.append({"name": run_path.name, "variants": variants})

    return runs


def render_html(runs: List[Dict[str, Any]]) -> str:
    style = """
    body {
        font-family: "Inter", "Segoe UI", system-ui, -apple-system, sans-serif;
        margin: 0;
        background: #0f172a;
        color: #e2e8f0;
    }
    header {
        text-align: center;
        padding: 2rem 1rem 1rem;
    }
    .container {
        max-width: 1100px;
        margin: 0 auto;
        padding: 1rem 1.5rem 3rem;
    }
    .run-card {
        background: #1e293b;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 25px rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(148, 163, 184, 0.15);
    }
    .run-title {
        font-size: 1.4rem;
        margin: 0 0 1rem;
        color: #f97316;
    }
    table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 1rem;
    }
    th, td {
        padding: 0.6rem 0.5rem;
        text-align: left;
        border-bottom: 1px solid rgba(148, 163, 184, 0.1);
    }
    th {
        font-size: 0.9rem;
        letter-spacing: 0.02em;
        text-transform: uppercase;
        color: #cbd5f5;
    }
    .tag {
        display: inline-flex;
        align-items: center;
        padding: 0.15rem 0.6rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .tag-pass {
        background: rgba(34, 197, 94, 0.15);
        color: #4ade80;
    }
    .tag-fail {
        background: rgba(248, 113, 113, 0.15);
        color: #fca5a5;
    }
    details {
        margin-top: 0.5rem;
        background: #0f172a;
        border-radius: 12px;
        padding: 0.5rem 0.8rem;
        border: 1px solid rgba(148, 163, 184, 0.15);
    }
    summary {
        cursor: pointer;
        font-weight: 600;
        outline: none;
    }
    pre {
        white-space: pre-wrap;
        overflow-x: auto;
        font-size: 0.85rem;
        background: transparent;
        margin-top: 0.8rem;
    }
    .empty {
        text-align: center;
        padding: 3rem;
        border: 2px dashed rgba(148, 163, 184, 0.3);
        border-radius: 16px;
        color: #94a3b8;
        font-size: 1.1rem;
    }
    """

    lines = [
        "<!DOCTYPE html>",
        "<html lang='en'>",
        "<head>",
        "<meta charset='utf-8' />",
        "<meta name='viewport' content='width=device-width, initial-scale=1' />",
        "<title>Daytona Code Ensemble – Run Summary</title>",
        f"<style>{style}</style>",
        "</head>",
        "<body>",
        "<header>",
        "<h1>Daytona Ensemble Run Summary</h1>",
        "<p>Overview of saved runs in the results/ directory.</p>",
        "</header>",
        "<div class='container'>",
    ]

    if not runs:
        lines.append(
            "<div class='empty'>No run artifacts found. Run the CLI to generate results.</div>"
        )
    else:
        for run in runs:
            lines.append("<section class='run-card'>")
            lines.append(f"<h2 class='run-title'>{html.escape(run['name'])}</h2>")
            lines.append("<table>")
            lines.append(
                "<tr><th>Variant</th><th>Status</th><th>Runtime (ms)</th>"
                "<th>Exit Code</th><th>Generation (ms)</th></tr>"
            )

            for variant in run["variants"]:
                res = variant["result"]
                status = "PASS" if res.get("passed") else "FAIL"
                tag_cls = "tag-pass" if res.get("passed") else "tag-fail"
                runtime = f"{res.get('runtime_ms', 0):.1f}"
                generation = f"{res.get('generation_ms', 0):.1f}"
                exit_code = res.get("exit_code", "")

                lines.append("<tr>")
                lines.append(f"<td>{html.escape(variant['name'])}</td>")
                lines.append(
                    f"<td><span class='tag {tag_cls}'>{status}</span></td>"
                )
                lines.append(f"<td>{runtime}</td>")
                lines.append(f"<td>{exit_code}</td>")
                lines.append(f"<td>{generation}</td>")
                lines.append("</tr>")
                lines.append("<tr>")
                lines.append("<td colspan='5'>")
                lines.append("<details>")
                lines.append("<summary>View solution & logs</summary>")

                if variant["solution"]:
                    lines.append("<h4>solution.py</h4>")
                    lines.append("<pre>")
                    lines.append(html.escape(variant["solution"]))
                    lines.append("</pre>")

                stdout = res.get("stdout", "")
                stderr = res.get("stderr", "")
                if stdout:
                    lines.append("<h4>stdout</h4>")
                    lines.append("<pre>")
                    lines.append(html.escape(stdout))
                    lines.append("</pre>")
                if stderr:
                    lines.append("<h4>stderr</h4>")
                    lines.append("<pre>")
                    lines.append(html.escape(stderr))
                    lines.append("</pre>")

                lines.append("</details>")
                lines.append("</td>")
                lines.append("</tr>")

            lines.append("</table>")
            lines.append("</section>")

    lines.extend(["</div>", "</body>", "</html>"])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render Daytona Code Ensemble results into a single HTML dashboard."
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=Path("results"),
        help="Directory containing run_* folders (default: results)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results_summary.html"),
        help="Where to write the generated HTML (default: results_summary.html)",
    )
    args = parser.parse_args()

    runs = load_runs(args.results_dir)
    html_text = render_html(runs)
    args.output.write_text(html_text, encoding="utf-8")
    print(f"Wrote summary for {len(runs)} run(s) to {args.output}")


if __name__ == "__main__":
    main()
