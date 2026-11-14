# Question 1: Cost Reduction for SupportCopilot

## Summary

| | Total points (T-1001 to T-1004) | Per ticket |
|---|---:|---:|
| Baseline | 35,544 | 8,886 |
| Optimized | **8,100** | **2,025** |

The optimized agent saves 27,444 points (a 77% reduction, about 4.4x cheaper) and is under the target of 3,000 points per ticket. `action` and `kb_article` are identical on all four public tickets, and the T-1091 hold-out still passes.

## Where the points were going

1. **Verbose reasoning prompt.** The instructions ("think step by step", "full reasoning", "quote any article") made the model write a 480+ token explanation. Output costs 15 points per token, so this was the largest cost.
2. **Unstable prefix.** A random run id at the top of the system prompt made every prefix unique, so prompt caching could never apply.
3. **Pretty-printed order JSON** (`indent=2`) added whitespace tokens.
4. **No cache hint.** The prompt never passed `cached_prefix` to the client.
5. **Unneeded output.** The prompt asked for `customer_reply`, which is not graded.

## Changes (all in `question1/agent.py`)

1. Asked for compact JSON with only `action` and `kb_article`, with no reasoning or quoting.
2. Removed the run id. The system prompt (rules, examples, help-center articles) is now a fixed constant, with the ticket thread and order snapshot placed last.
3. Compacted the order snapshot with `separators=(",", ":")`. All fields are kept, because routing depends on them.
4. Passed the static system prompt as `cached_prefix`.
5. Kept exactly one LLM call per ticket, with no retries. `parse_resolution` is unchanged, so parsing still works.

## Per-call breakdown

`points = uncached_input x 3 + cached_input x 0.3 + output x 15`

| Ticket | Uncached input | Cached input | Output | Points |
|---|---:|---:|---:|---:|
| T-1001 | 487 | 0 | 46 | 2,151 |
| T-1002 | 479 | 0 | 39 | 2,022 |
| T-1003 | 466 | 0 | 39 | 1,983 |
| T-1004 | 468 | 0 | 36 | 1,944 |
| **Total** | | | | **8,100** |

Worked example (T-1001): 487 x 3 + 0 x 0.3 + 46 x 15 = 1,461 + 0 + 690 = 2,151.

Reproduce with `python question1/breakdown.py`.

## Trade-offs and limitations

- **Cache is not active.** The static prefix is 374 tokens, below the 1,024-token minimum, so all input is billed at 3 points per token. I could pad the prefix past 1,024, but with a help center this small that would add text only to earn the discount, and the target is already met.
- **Full help center kept in the prompt.** Filtering articles by keyword is fragile. A filter that missed the right article would fail on the subscription hold-out (T-1091) and on hidden tickets.
- **Output size is fixed by the local simulator**, so output tokens could not be tuned here. On a real API I would also set `max_tokens`.
- **First-call caching.** The simulator credits a cached prefix on the first call. On a real API the first call would be a cache write, and savings would appear from the second call onward.
- **`test_baseline_cost_is_high` now fails by design.** It asserts the baseline cost is above 15,000. I left the test unchanged rather than weaken it.

## Verification

- `python question1/run.py` returns the same `action` and `kb_article` as the baseline for T-1001 to T-1004.
- `python -m pytest -q`: the correctness tests, including the T-1091 hold-out, pass. Only the baseline-cost test fails, as expected.
