# Research notes

4 November 2026. Local preparation plus a four-episode live smoke test. No full-study findings yet.

I want to test whether an agent keeps acting on an earlier permission after the user withdraws it. The narrower comparison is whether moving that withdrawal later in an email-preparation task changes the unauthorized send rate.

The useful distinction is between what the agent says and what it does. If it says it will save a draft but then calls send_email, the tool attempt is the evidence. If an external gate blocks the send, that protects the workspace but does not mean the agent made the right decision.

## What is ready

The local runner, simulated tools, deterministic scoring, scenario split, reference policies, and offline checks are implemented. Validation status is recorded separately in VALIDATION.md after running those checks.

## What is not known

The Modal adapter now has a successful real-provider smoke test: one family across four conditions, with no unauthorized attempts observed. See SMOKE_TEST.md for exact usage and limits. I do not know whether a larger evaluation will reveal failures, whether late revocation is harder than early revocation, or whether the reminder helps.

## What I can defend about the design

The retained-permission condition catches an agent that simply refuses to send anything. The initial-prohibition condition distinguishes a general problem following delivery instructions from a problem introduced by a changed permission. Early versus late revocation tests timing while keeping the initial and final prompts the same.

The scorer uses explicit tool events and known permission transitions. I can test it with manually specified trajectories rather than asking another LLM to decide whether the agent was safe. The email-body check is weaker: it verifies required tokens, so a human still needs to check whether the text uses them correctly.

## Main uncertainty in interpretation

Late revocation changes several things at once: how long the old permission remains in context, how much preparation happens before the change, and how recently the agent sees the change. If late revocation produces more errors, I can report a timing effect. I cannot conclude that plan commitment caused it without a separate intervention.

The workflow is also short and synthetic. Forty parameterized families are still one workflow template. I would rather report that limit directly than describe this as a general benchmark of agent safety.

## Questions for the discussion

What do current evaluations miss? For this study, I am focusing on permission changing within a task, and on unauthorized intermediate actions that a final response or final state alone might miss. Existing work already studies authorization and revocation, so the point is a controlled measurement, not claiming the whole problem is unexplored.

How would I evaluate changing behavior? Keep the environment and task paired, change when the permission update arrives, log the actual actions, and compare repeated runs within task families.

How would I know the evaluation is correct? Start with literal oracle fixtures and faulty reference policies, then audit real trajectories against the user messages and tool-state transitions. Keep scorer correctness separate from whether the synthetic task represents real use.

## Results and analysis

The first live smoke test completed all four episodes using 43,488 provider-reported tokens. The agent sent only in the retained-permission condition. This is a workflow check, not enough evidence to assess the timing hypothesis. The full pilot and heldout study remain pending; observed usage means the earlier full-study token estimate needs revision before proceeding.
