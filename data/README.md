# Data layout

## `prompts/`

Original batch prompts, as used in the closed-book protocol:

- `prompts/round1/` — nine batches (math, citations, false premises, obscure facts)
- `prompts/round2/` — ten batches (harder math and proof checking, fabricated
  literature, niche citations, exact paper numbers, and pushback follow-ups)

To compare with the released `qwen4-max-preview` baseline, run these batch
files (see `manifest.json` and `scripts/run_eval.py`). Do not split them
unless you are deliberately running a per-item protocol.

The two pushback follow-up files (`pressure_math_t2.txt`,
`pressure_fake_t2.txt`) already contain an evaluator-written reconstruction
of the previous turn. That is what the baseline was given. For a live
multi-turn rerun you may instead feed the model's actual first-turn output.

## `items.jsonl`

One JSON object per scored item (63 lines). Fields:

| Field | Meaning |
| --- | --- |
| `id` | Stable id, e.g. `r1-M2`, `r2-Q1`, `r2-pressure-math-t2` |
| `round` | `1` or `2` |
| `category` | `math`, `citation`, `false_premise`, `obscure_facts`, `exact_numbers`, or `pushback` |
| `subcategory` | Finer type (optional scoring hint) |
| `item_tag` | Tag as it appears in the prompt, e.g. `M14`, `F10` |
| `batch_id` | Source batch name (`math1`, `fabricated`, …) |
| `source_file` | Path of the original batch prompt |
| `prompt` | A standalone prompt: the batch rules plus this item only. For citation tasks and pushback follow-ups this is the full original file. |
| `prompt_item` | The item stem (or the full file, when the item is the whole batch) |
| `gold` | Gold answer or the expected bibliographic / behavioral target |
| `expected_behavior` | What a correct response must do |
| `scoring_notes` | Edge cases, partial-credit notes, and known traps |
| `answer_type` | Coarse answer kind (`exact_integer`, `reject_false_premise`, …) |

Citation *prompts* are stored as five records (one per topic). Each prompt
asks for up to five real papers, so the headline citation metric is still
“papers listed, not fabricated” (25 requested slots in the baseline).

Pushback is stored as three records (math turn 1, math turn 2, fake-paper
turn 2) corresponding to two scenarios in the score tables.

## `manifest.json`

Lists each batch file and the item ids it contains, in the original run order.
