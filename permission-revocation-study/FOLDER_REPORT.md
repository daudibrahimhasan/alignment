# Local folder inventory and cleanup report

Project folder: D:\AI Safety\Tess

Keep: results/ (raw evidence, interrupted records, manifests, analyses, audit queue); snapshots/ (frozen source provenance); scenarios*.json; experiment.py, analyze.py, report_study.py, package_study.py, study_dataset.py and test_experiment.py; protocol, validation, pilot and recovery notes; STUDY_REPORT.md/.pdf, STUDY_RESULTS.json and heldout_results.png.

Private: keep .env locally only. Never include it in a shared archive.

Safe to regenerate or remove later: __pycache__/ and PDF preview images. Tess_Revocation_Experiment.zip is a shareable export that can be regenerated. CHECKSUMS.sha256 at the project root predates the final study and should not be treated as the final integrity manifest; the regenerated ZIP contains its own current checksums.

Do not clean raw trajectories, interruptions, manifests, resume logs, or snapshots: these explain the recovery and preserve the study evidence.

C: check: the task-specific visualization folder supplied with this chat contains no files. All newly created project artifacts, report attachments and previews are stored under this dedicated D: folder. Codex runtime files, chat history and system fonts on C: are application-managed dependencies, not project outputs; they were not moved or deleted.


Also keep: render_report.py (rebuilds the Times New Roman PDF), REVIEW_STATUS.md (review provenance), and results/live-v2-heldout/assistant_audit.csv (18-episode assistant review). previews/ and pdf-preview-*.png can be regenerated.

Inventory snapshot, 4 November 2026. Sizes below precede final PDF/ZIP regeneration.

| Folder/file | Size (bytes) |
| --- | ---: |
| .env | 213 |
| .gitignore | 41 |
| __pycache__ | 105,201 |
| analyze.py | 6,059 |
| AUDIT_TEMPLATE.csv | 196 |
| CHECKSUMS.sha256 | 33,090 |
| experiment.py | 31,006 |
| FOLDER_REPORT.md | 2,179 |
| heldout_results.png | 77,920 |
| package_study.py | 3,401 |
| pdf-preview-1.png | 49,526 |
| pdf-preview-2.png | 58,783 |
| pdf-preview-3.png | 26,945 |
| pdf-preview-4.png | 43,547 |
| pdf-preview-5.png | 9,069 |
| PILOT_DECISION.md | 3,468 |
| previews | 268,144 |
| PROTOCOL.md | 10,718 |
| PROTOCOL_V2.md | 5,964 |
| README.md | 7,670 |
| render_report.py | 2,298 |
| report_study.py | 13,502 |
| RESEARCH_NOTES.md | 3,763 |
| results | 6,771,636 |
| REVIEW_STATUS.md | 385 |
| scenarios.json | 13,480 |
| scenarios_v2.json | 22,685 |
| SMOKE_TEST.md | 2,395 |
| snapshots | 215,688 |
| study_dataset.py | 6,377 |
| STUDY_REPORT.md | 11,043 |
| STUDY_REPORT.pdf | 103,684 |
| STUDY_RESULTS.json | 4,068 |
| Tess_Revocation_Experiment.zip | 1,630,588 |
| test_experiment.py | 15,370 |
| TRANSPORT_RECOVERY.md | 2,516 |
| VALIDATION.md | 2,573 |
