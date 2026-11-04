# Permission revocation study

I used a simulated email task to test whether an agent respects a change in permission over multiple turns. The question was whether revoking permission later would produce more unauthorized sends.

## Start here

- [Research note](handoff/research-note.docx): design, results, one failure and its passing repeat, and limitations.
- [Full report](STUDY_REPORT.md) and [PDF](STUDY_REPORT.pdf).
- [Example failure](results/live-v2-heldout/trajectories/v2-decision-2-early-0.md) and [passing repeat](results/live-v2-heldout/trajectories/v2-decision-2-early-1.md).
- [Protocol](PROTOCOL_V2.md), [pilot decision](PILOT_DECISION.md) and [transport recovery](TRANSPORT_RECOVERY.md).

## Results

Fifteen heldout cases covered five workflow templates. Each case had four permission conditions and two repetitions, giving 120 episodes. A separate 20 episode development pilot preceded the heldout run.

| Condition | Unauthorized send episodes | Narrow task completions |
| --- | ---: | ---: |
| Permission retained | 0/30 | 30/30 |
| Draft only from the start | 2/30 | 28/30 |
| Early revocation | 1/30 | 29/30 |
| Late revocation | 0/30 | 30/30 |

The predicted increase after later revocation was not supported. All three failures followed the final generic instruction to finish under current delivery instructions. That wording may have acted as an implicit authorization cue. The data do not isolate a memory or commitment mechanism.

The completion metric checks permission adherence, recipient, subject and required fact tokens. It does not establish fully correct prose. All 120 prompt sequences, scores and tool states were checked. The 18 episode semantic review was performed by an assistant; independent human review remains outstanding. The [audit records](results/live-v2-heldout/assistant_audit.csv) preserve that provenance.

## Inspect the saved evidence

The runner and scorer require Python 3.11 or later and use the standard library. From this folder:

```powershell
python analyze.py results/live-v2-heldout
```

This recomputes scores and replays saved tool events without making model requests. It regenerates the automated analysis and an empty review queue; the completed assistant audit is stored separately.

```powershell
python -m unittest -v
python experiment.py --backend scripted-compliant --output results/new-scripted-check
```

Scripted policies check the harness. They are not model findings. Use a new output directory for each fresh run.

## Run a new live experiment

The supplied endpoint identified the model as `deepseek-ai/DeepSeek-V4.1-Flash`; its weights were not independently verified. The private endpoint is redacted from this repository. Configure a tool-capable Chat Completions endpoint using the runner's `--base-url`, `--model` and authentication options. Credentials belong in a local `.env`, using the empty [.env.example](.env.example) as a guide.

Example for a separately configured endpoint:

```powershell
python experiment.py --dataset scenarios_v2.json --backend api --base-url https://YOUR-ENDPOINT/v1 --model YOUR-MODEL --split heldout --families 15 --repeats 2 --workers 2 --max-total-tokens 2335000 --max-api-calls 3600 --timeout 600 --output results/new-heldout-run
```

This command makes paid or metered inference requests. It creates a new study run; a different provider is not a continuation of the saved experiment. See `python experiment.py --help` for options.

## Files

`experiment.py` contains the runner, tools, permission scorer and aggregation. `scenarios_v2.json` contains the expanded study cases; `study_dataset.py` is their generator. `analyze.py` recomputes scores and replays state. `test_experiment.py` contains offline fixtures and mocked protocol checks.

`results/` contains the live and scripted evidence with separate labels. `snapshots/` preserves the frozen source and historical protocols, including status and budget statements from earlier stages. Recovery records document timeouts, checkpoint preserving resumes and the final switch from four workers to two.

`report_study.py` generates an automated report draft and a figure. The curated report includes qualitative review sections; see [REVIEW_STATUS.md](REVIEW_STATUS.md). Optional figure generation requires matplotlib. `render_report.py` rebuilds the report PDF using reportlab, PyMuPDF and Times New Roman at the configured Windows font paths. The rendered PDF is included for convenience.

The next experiment would vary the final completion message and compare a permission-state gate while reporting attempted and executed violations separately. Neither live comparison has run.
