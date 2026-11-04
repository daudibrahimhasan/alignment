# Permission changes in a multi turn email agent

I tested whether an email agent would keep acting on an earlier permission after the user withdrew it. I expected later revocation to cause more unauthorized sends. The 120 heldout episodes did not support that prediction.

Three episodes sent without authorization: two were draft only from the start, and one had an explicit early revocation. All three sends followed the final generic completion message. Each failing case passed in its other repetition.

[Read the research note](permission-revocation-study/handoff/research-note.docx) · [Full findings](permission-revocation-study/STUDY_REPORT.md) · [Code and reproduction](permission-revocation-study/)

The study uses a simulated email workspace. No real email was sent by the experiment. Raw trajectories, scoring logic, protocols and review records are included.
