# Permission revocation study

Start with [Research note for Tess](handoff/Research%20note%20for%20Tess.docx), the [full report](STUDY_REPORT.md), or the [PDF](STUDY_REPORT.pdf). Personal preparation notes are in [handoff/](handoff/).

The planned 120 heldout episodes are complete. Unauthorized-send episodes were 0/30 retained, 2/30 never-authorized, 1/30 early revocation and 0/30 late revocation. The predicted increase after later revocation was not supported. All email actions in the experiment were simulated.

This public export redacts the private endpoint and excludes credentials. Frozen snapshots preserve historical instructions and code; their earlier status statements are historical. The original live output paths already exist, so use a new directory for a fresh run. Do not resume the public export against a different provider as though it were the original study.

The runner and scorer use the Python standard library. Optional figure generation needs matplotlib; PDF generation needs reportlab and PyMuPDF plus Times New Roman font files at the configured Windows paths. Rendered report artifacts are included. See REVIEW_STATUS.md for automated versus assistant-reviewed content.

# Does an agent stop when permission changes?

A small controlled experiment on explicit permission revocation in multi-turn email preparation. Everything happens in a simulated workspace. No real email is sent.

**Status: 20 pilot and 120/120 heldout episodes complete. See STUDY_REPORT.md and STUDY_REPORT.pdf for findings.** See [SMOKE_TEST.md](SMOKE_TEST.md) for usage and limitations. The planned heldout run is complete. Scripted examples validate the harness and are not evidence about LLM behavior.

The expanded study uses [PROTOCOL_V2.md](PROTOCOL_V2.md), five preparation workflows, and a 20-episode development pilot followed by 120 heldout episodes. [PILOT_DECISION.md](PILOT_DECISION.md) records the decision to proceed without changing prompts. [PROTOCOL.md](PROTOCOL.md) preserves the original plan; [RESEARCH_NOTES.md](RESEARCH_NOTES.md) tracks the evidence.

V2 execution (each output directory must be new):

```powershell
python experiment.py --dataset scenarios_v2.json --backend api --auth modal --model deepseek-ai/DeepSeek-V4.1-Flash --families 5 --workers 4 --max-total-tokens 400000 --max-api-calls 600 --output results/live-v2-pilot
python experiment.py --dataset scenarios_v2.json --backend api --auth modal --model deepseek-ai/DeepSeek-V4.1-Flash --split heldout --families 15 --repeats 2 --workers 4 --max-total-tokens 2400000 --max-api-calls 3600 --output results/live-v2-heldout
python report_study.py
python package_study.py
```

Four episode workers share a synchronized request meter and token reservations. The reservation uses input bytes plus the requested completion limit and framing allowance; it is conservative, not an exact provider tokenizer. An error or exhausted budget stops new requests while saving active episode traces. The user's revised budget permits roughly 2.7 million overall tokens. See the pilot decision for measured use and the operational cap.

An interrupted batch can be continued with the same arguments and `--resume --timeout 180`. Completed episodes are skipped; interrupted conversations retain their original messages and workspace state. Original interrupted records are archived, the manifest stays unchanged, and a resume-session log records the new code hash and timeout. The token/request meters carry over, and per-checkpoint response limits are not reset. This explicit recovery is not a silent fresh rerun or selection of a better outcome.

## Run without an API key

Python 3.11 or later. No dependencies to install. From this folder:

```powershell
python -m unittest -v
python experiment.py --backend scripted-compliant --output results/check-compliant
python experiment.py --backend scripted-stale --output results/check-stale
python experiment.py --backend scripted-stale --intervention gate --output results/check-gate
python analyze.py results/check-stale
```

Each output folder must be new. It contains a manifest, summary, and JSON plus readable Markdown for each trajectory. The compliant policy should complete all four conditions. The deliberately stale policy sends despite early and late revocations. The gate blocks those sends while preserving attempted-violation labels.

`scenarios.json` contains the frozen v1 data, generated deterministically by `experiment.generate()`. The split has 10 development and 30 heldout families; all share one workflow template. The generator is checked against the committed data by the tests.

## Run later with a key

Alternatively, put your key in the local `.env` file as `OPENAI_API_KEY="your-key"`. The runner loads this file automatically; existing environment variables take precedence. `.env` is excluded from Git and must stay out of shared packages.

For the supplied Modal endpoint, keep `MODAL_CHADNI_PROXY_TOKEN_ID`, `MODAL_CHADNI_PROXY_TOKEN_SECRET`, and `MODAL_CHADNI_ENDPOINT_URL` in `.env`. Use `--auth modal`; the runner reads the endpoint and sends the proxy credentials only in headers. For example:

```powershell
python experiment.py --backend api --auth modal --model deepseek-ai/DeepSeek-V4.1-Flash --families 1 --max-api-calls 100
```

The model ID above was returned by this endpoint's `/v1/models` discovery on 4 November 2026. It is a served identifier, not an independent verification of the model weights. [Modal proxy authentication](https://modal.com/docs/guide/webhook-proxy-auth).

The live adapter uses the documented Chat Completions function-tool protocol. Use a model and endpoint that support that protocol. A provider-specific adapter or a Responses adapter may be needed for models that do not support it. The live adapter was exercised in the saved smoke, development and heldout runs; see the transport recovery notes for timeouts.

Enter your key locally without saving it in a file or this chat:

```powershell
$credential = Read-Host 'API key' -AsSecureString
$env:OPENAI_API_KEY = [System.Net.NetworkCredential]::new('', $credential).Password
$modelId = Read-Host 'Tool-capable model ID'
python experiment.py --backend api --model $modelId --families 1 --max-api-calls 100
Remove-Item Env:OPENAI_API_KEY
```

For another HTTPS Chat Completions-compatible provider, set `--base-url` and, if needed, `--key-env` to the environment variable holding its key. Credentials are not written into manifests. Do not send a key to an endpoint you do not trust. Provider error bodies are not saved because they can echo credentials.

After the smoke test and development pilot, review token usage and freeze the protocol before a heldout run. Example commands (substitute your chosen model ID):

```powershell
python experiment.py --backend api --model $modelId --families 10 --repeats 2 --max-api-calls 2400
python experiment.py --backend api --model $modelId --split heldout --families 30 --repeats 3 --max-api-calls 10800
python experiment.py --backend api --model $modelId --split heldout --families 30 --repeats 3 --intervention reminder --max-api-calls 10800
```

The maximum request count is a ceiling, not a budget estimate. Each model/intervention run is separate. API errors stop the batch and preserve incomplete evidence. There is no automatic retry. For interrupted v2 batches, use the documented --resume recovery; complete episodes are skipped and observed conversation state is preserved. Do not merge repeated batches without checking duplicate family/condition/repetition IDs.

## Files and evidence

- `experiment.py`: scenarios, tools, simulated workspace, scorer, API adapter, runner and family-paired analysis.
- `test_experiment.py`: literal oracle fixtures, offline runner checks and mocked API protocol checks.
- `analyze.py`: re-score saved trajectories, replay tool state, report missing-outcome bounds, and create a manual audit queue.
- `results/validation-*`: labeled scripted demonstrations only.
- `AUDIT_TEMPLATE.csv`: manual review fields for real trajectories.

JSON scores are reproducible with `experiment.score(record)`. Summaries are reproducible with `experiment.summarize(records)`; keep models and interventions separate. The CLI itself only aggregates one configuration per output folder.

The runner saves returned model IDs and token usage per response. It randomizes episode order, logs prompt/data/code hashes, and has per-checkpoint and global call caps. It does not guarantee reproducible provider sampling. The artifact check verifies exact destination/subject and required fact tokens, not full prose correctness.

API schema references checked 4 November 2026: [Chat Completions](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create), [function calling](https://developers.openai.com/api/docs/guides/function-calling).
