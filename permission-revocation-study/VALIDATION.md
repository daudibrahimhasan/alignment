# Offline validation

Verified 4 November 2026 with Python 3.11.9. No API key was used. No inference requests or real emails were sent.

24 tests passed with `python -m unittest -v`. They cover independent expected permission labels, boundary timing, invalid and blocked attempts, premature sends, artifact token boundaries, incomplete runs, duplicate sends, missing-outcome bounds, state replay, and mocked API request construction.

Three full development-split batches completed: 10 families x 4 conditions each, 120 scripted episodes total. All saved scores were recomputed and all tool-state transitions replayed successfully. These are deliberately programmed policies, not model observations.

| Reference policy | Episodes | Episodes with unauthorized attempts | Blocked sends | Executed sends | Authorized completions |
| --- | ---: | ---: | ---: | ---: | ---: |
| Compliant | 40 | 0 | 0 | 10 | 40 |
| Stale permission | 40 | 20 | 0 | 30 | 20 |
| Stale permission with gate | 40 | 20 | 20 | 10 | 20 |

The stale policy is intentionally written to ignore revocation. Its failures prove that the scorer catches this programmed behavior. They say nothing about whether any LLM behaves this way. The gate demonstration checks that blocked execution does not erase an attempted violation.

Readable examples:

- [Compliant late-revocation trajectory](results/validation-compliant/trajectories/email-00-late-0.md)
- [Stale-permission trajectory](results/validation-stale/trajectories/email-00-late-0.md)
- [The same programmed failure with a gate](results/validation-gate/trajectories/email-00-late-0.md)

Full automated reports:

- [Compliant policy](results/validation-compliant/REPORT.md)
- [Stale policy](results/validation-stale/REPORT.md)
- [Gate baseline](results/validation-gate/REPORT.md)

Manual audit queues exist for each batch; their fields are intentionally blank. No human review is implied by automated replay. This section records the original offline validation; later live evidence is reported separately.

## V2 validation update

Before the v2 pilot, 28 checks passed, including synchronized token metering, budget reservation, all v2 scenario/condition pairs, and parallel scripted execution. A 20-episode parallel scripted batch completed and is saved under results/validation-v2-parallel. A later transport-recovery check verifies that resuming a conversation preserves earlier messages, tool state, call IDs and checkpoint limits without rerunning completed work. See TRANSPORT_RECOVERY.md for the observed provider timeout and recovery record.
