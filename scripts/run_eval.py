#!/usr/bin/env python3
"""Run llm-math-hallucination-bench against an OpenAI-compatible chat endpoint.

The official protocol uses the original *batch* prompt files under
data/prompts/ (several items per call), not the per-item JSONL lines.
Follow-up / pushback prompts are stored as standalone files that already
contain a reconstructed previous turn; this runner does not automatically
chain model outputs.

Required environment variables (no defaults that point at a real vendor):

    BASE_URL   OpenAI-compatible base, e.g. https://api.example.com/v1
    API_KEY    secret; never written to disk or stdout
    MODEL      model name as the server expects it

Optional:

    TEMPERATURE   default 0
    TIMEOUT_SEC   default 300

Example:

    export BASE_URL="https://api.example.com/v1"
    export API_KEY="..."
    export MODEL="your-model"
    python scripts/run_eval.py --out results/your-model

The API key is read from the environment and only sent in the Authorization
header. It is never printed, and it is not stored in the written .meta files.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROMPTS = ROOT / "data" / "prompts"

# Original evaluation order (parallel batches are still listed in start-time order).
ROUND_BATCHES = {
    1: [
        "math1",
        "math2",
        "math3",
        "math4",
        "cite_worldmodels",
        "cite_diffusion",
        "cite_gnn",
        "false_premise",
        "obscure_facts",
    ],
    2: [
        "math_a",
        "math_b",
        "math_c",
        "fabricated",
        "cite_prove",
        "cite_pde",
        "exact_nums",
        "pressure_math_t1",
        "pressure_math_t2",
        "pressure_fake_t2",
    ],
}


def eprint(*args: object) -> None:
    print(*args, file=sys.stderr)


def require_env(name: str) -> str:
    val = os.environ.get(name, "").strip()
    if not val:
        eprint(f"error: environment variable {name} is not set")
        sys.exit(2)
    return val


def chat_completion(base_url: str, api_key: str, model: str, prompt: str,
                    temperature: float, timeout: float) -> str:
    url = base_url.rstrip("/") + "/chat/completions"
    body = {
        "model": model,
        "temperature": temperature,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
    }
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + api_key,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        # Do not print request headers (they contain the key) or the raw body
        # if it might echo authorization data back.
        eprint(f"error: HTTP {exc.code} from the chat completions endpoint")
        try:
            err_body = exc.read().decode("utf-8", errors="replace")
        except Exception:
            err_body = ""
        # Redact anything that looks like a key before showing a short excerpt.
        redacted = err_body.replace(api_key, "[REDACTED]")
        eprint(redacted[:500] if redacted else "(no body)")
        raise SystemExit(1) from None
    except urllib.error.URLError as exc:
        eprint(f"error: request failed ({exc.reason!s})")
        raise SystemExit(1) from None

    try:
        content = payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        eprint("error: unexpected response shape (missing choices[0].message.content)")
        raise SystemExit(1) from None
    if not isinstance(content, str):
        eprint("error: message content is not a string")
        raise SystemExit(1)
    return content


def write_meta(path: Path, name: str, start: float, end: float, out_bytes: int,
               model: str, exit_code: int) -> None:
    start_h = time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime(start))
    end_h = time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime(end))
    lines = [
        f"name={name}",
        f"model={model}",
        f"start={start_h}",
        f"end={end_h}",
        f"start_epoch={start:.9f}",
        f"end_epoch={end:.9f}",
        f"exit={exit_code}",
        f"latency_sec={end - start:.3f}",
        f"out_bytes={out_bytes}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def batches_for(rounds: list[int]) -> list[tuple[int, str, Path]]:
    out = []
    for rnd in rounds:
        for name in ROUND_BATCHES[rnd]:
            path = PROMPTS / f"round{rnd}" / f"{name}.txt"
            if not path.is_file():
                eprint(f"error: missing prompt file {path}")
                raise SystemExit(2)
            out.append((rnd, name, path))
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    parser.add_argument("--round", choices=("1", "2", "both"), default="both",
                        help="which evaluation round to run (default: both)")
    parser.add_argument("--out", type=Path, required=True,
                        help="directory to write round*/NAME.out and .meta into")
    parser.add_argument("--only", nargs="*", default=None,
                        help="optional subset of batch names, e.g. math1 fabricated")
    parser.add_argument("--dry-run", action="store_true",
                        help="list the batches that would be run and exit")
    args = parser.parse_args()

    rounds = [1, 2] if args.round == "both" else [int(args.round)]
    jobs = batches_for(rounds)
    if args.only:
        wanted = set(args.only)
        jobs = [j for j in jobs if j[1] in wanted]
        missing = wanted - {j[1] for j in jobs}
        if missing:
            eprint("error: unknown batch name(s): " + ", ".join(sorted(missing)))
            raise SystemExit(2)

    if args.dry_run:
        for rnd, name, path in jobs:
            print(f"round{rnd}\t{name}\t{path}")
        return

    base_url = require_env("BASE_URL")
    api_key = require_env("API_KEY")
    model = require_env("MODEL")
    try:
        temperature = float(os.environ.get("TEMPERATURE", "0"))
        timeout = float(os.environ.get("TIMEOUT_SEC", "300"))
    except ValueError:
        eprint("error: TEMPERATURE and TIMEOUT_SEC must be numbers")
        raise SystemExit(2)

    out_root = args.out if args.out.is_absolute() else (Path.cwd() / args.out)
    for rnd, name, path in jobs:
        dest_dir = out_root / f"round{rnd}"
        dest_dir.mkdir(parents=True, exist_ok=True)
        prompt = path.read_text(encoding="utf-8")
        print(f"running round{rnd}/{name} ...", flush=True)
        start = time.time()
        try:
            text = chat_completion(base_url, api_key, model, prompt, temperature, timeout)
            exit_code = 0
        except SystemExit:
            end = time.time()
            write_meta(dest_dir / f"{name}.meta", name, start, end, 0, model, 1)
            raise
        end = time.time()
        out_path = dest_dir / f"{name}.out"
        out_path.write_text(text, encoding="utf-8")
        write_meta(dest_dir / f"{name}.meta", name, start, end, out_path.stat().st_size,
                   model, exit_code)
        print(f"  done in {end - start:.3f}s, wrote {out_path}", flush=True)


if __name__ == "__main__":
    main()
