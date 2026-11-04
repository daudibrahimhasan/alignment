"""Build the final note and figure from saved, re-scored live evidence."""
import csv
import hashlib
import json
from pathlib import Path
import statistics

import analyze
import experiment as e


def load(folder):
    return [json.loads(p.read_text(encoding='utf-8')) for p in sorted((folder/'trajectories').glob('*.json'))]


def usage(records):
    totals = {k: 0 for k in ('prompt_tokens', 'completion_tokens', 'total_tokens')}
    calls = 0
    for record in records:
        for event in record['events']:
            if event['type'] == 'assistant':
                calls += 1
                values = event['metadata'].get('usage') or {}
                for key in totals:
                    totals[key] += values.get(key, 0)
    return {**totals, 'requests': calls}


def workflow_rows(records):
    rows = []
    for workflow in sorted({r['family']['workflow_id'] for r in records}):
        group = [r for r in records if r['family']['workflow_id'] == workflow]
        rows.append({'workflow': workflow, 'episodes': len(group),
                     'unauthorized': sum(r['scores']['unauthorized_attempt'] for r in group),
                     'completed': sum(r['scores']['authorized_completion'] for r in group)})
    return rows


def reliability(records):
    rows = []
    for condition in e.CONDITIONS:
        pairs = []
        for family in sorted({r['family']['id'] for r in records}):
            group = [r for r in records if r['condition'] == condition and r['family']['id'] == family]
            if len(group) == 2 and all(r['scores']['evaluable'] for r in group):
                pairs.append(group)
        rows.append({'condition': condition, 'complete_two_run_cases': len(pairs),
                     'unauthorized_discordant_cases': sum(p[0]['scores']['unauthorized_attempt'] != p[1]['scores']['unauthorized_attempt'] for p in pairs),
                     'completion_discordant_cases': sum(p[0]['scores']['authorized_completion'] != p[1]['scores']['authorized_completion'] for p in pairs)})
    return rows


def workflow_contrast(records):
    # Equal-weight workflow estimates: only five clusters, not fifteen independent task types.
    values = []
    for workflow in sorted({r['family']['workflow_id'] for r in records}):
        group = [r for r in records if r['family']['workflow_id'] == workflow]
        summary = e.summarize(group)
        value = summary['primary_contrast']['late_minus_early']
        if value is not None:
            values.append({'workflow': workflow, 'late_minus_early': value})
    return values


def figure(records, path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    rows = e.summarize(records)['conditions']
    labels = ['Retained', 'Never allowed', 'Early revocation', 'Late revocation']
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.6), layout='constrained')
    for ax, key, title, color in [(axes[0], 'unauthorized_observed_all', 'Episodes with unauthorized send attempts', '#a43b32'),
                                  (axes[1], None, 'Completed under current permission', '#285f85')]:
        counts = [row[key] if key else sum(r['scores']['authorized_completion'] for r in records if r['condition'] == row['condition']) for row in rows]
        ax.bar(range(4), counts, color=color, width=.6)
        ax.set_xticks(range(4), labels, rotation=18, ha='right')
        ax.set_ylim(0, max(row['n'] for row in rows) * 1.18)
        ax.set_title(title, loc='left', fontsize=11)
        ax.set_ylabel('Episode count')
        ax.spines[['top', 'right']].set_visible(False)
        for i, (value, row) in enumerate(zip(counts, rows)):
            ax.text(i, value + .5, f"{value}/{row['n']}", ha='center', fontsize=10)
    fig.suptitle('Heldout email-agent evaluation | one served model, five workflow templates', fontsize=12)
    fig.savefig(path, dpi=180)
    plt.close(fig)


def main():
    root = e.ROOT
    pilot_folder = root/'results/live-v2-pilot'
    heldout_folder = root/'results/live-v2-heldout'
    pilot_summary = analyze.analyze(pilot_folder)
    summary = analyze.analyze(heldout_folder)
    pilot, records = load(pilot_folder), load(heldout_folder)
    smoke = load(root/'results/live-modal-smoke-v1')
    manifest = json.loads((heldout_folder/'manifest.json').read_text(encoding='utf-8'))
    totals = {name: usage(group) for name, group in [('smoke', smoke), ('development', pilot), ('heldout', records)]}
    workflows, repeats = workflow_rows(records), reliability(records)
    e.write_json(root/'STUDY_RESULTS.json', {'heldout': summary, 'workflow_counts': workflows,
                  'workflow_contrasts': workflow_contrast(records), 'repeat_consistency': repeats, 'usage': totals,
                  'planned_heldout_episodes': len(manifest['jobs']), 'saved_heldout_episodes': len(records)})
    all_tokens = sum(x['total_tokens'] for x in totals.values())
    violations = [r for r in records if r['scores']['unauthorized_attempt']]
    late = [r for r in violations if r['condition'] == 'late']
    early = [r for r in violations if r['condition'] == 'early']
    never = [r for r in violations if r['condition'] == 'never']
    lines = ['# Permission changes in a multi-turn email agent', '',
             'Research note, 4 November 2026. One endpoint-served model; simulated email only.', '',
             '## What I tested', '',
             'I tested whether an agent would keep following an earlier delivery permission after the user withdrew it, '
             'and whether moving that withdrawal later changed the failure rate. Each case had four conditions: '
             'permission retained, draft-only from the start, early revocation, and late revocation. '
             'I scored actual send_email tool attempts rather than whether the agent said it understood.', '',
             f'The heldout run saved {len(records)} of {len(manifest["jobs"])} planned episodes: '
             '15 cases across five preparation workflows, four conditions and two fresh runs per case/condition. '
             'The model identifier reported by the supplied Modal endpoint was deepseek-ai/DeepSeek-V4.1-Flash; '
             'I did not independently verify its weights. Each episode used an isolated workspace, with four episodes running concurrently.', '',
             '## Heldout results', '',
             '| Condition | Episodes | Complete trajectories | Unauthorized-attempt episodes | Authorized task completions |',
             '| --- | ---: | ---: | ---: | ---: |']
    for row in summary['conditions']:
        passes = sum(r['scores']['authorized_completion'] for r in records if r['condition'] == row['condition'])
        lines.append(f"| {row['condition']} | {row['n']} | {row['complete']} | {row['unauthorized_observed_all']} | {passes} |")
    contrast = summary['primary_contrast']
    lines += ['', f"Late minus early unauthorized-attempt rate: {contrast['late_minus_early']}; "
              f"case-family bootstrap 95% interval: {contrast['bootstrap_95_interval']}. "
              'This interval is conditional on the five shared templates. It is not a population-level safety guarantee, '
              'and a zero-width interval at zero does not establish zero risk.', '',
              f"Missing-outcome sensitivity bounds over all planned early/late pairs: {summary['missing_outcome_bounds_late_minus_early']}.", '',
              f'There were {len(early)} early-revocation, {len(late)} late-revocation and {len(never)} '
              'initial-prohibition episodes with unauthorized attempts. Initial-prohibition failures are a control result, '
              'not evidence that permission revocation caused the failure.', '',
              '![Heldout condition counts](heldout_results.png)', '',
              '### Workflows and repeated runs', '',
              '| Workflow | Episodes | Unauthorized-attempt episodes | Authorized completions |',
              '| --- | ---: | ---: | ---: |']
    for row in workflows:
        lines.append(f"| {row['workflow']} | {row['episodes']} | {row['unauthorized']} | {row['completed']} |")
    lines += ['', '| Condition | Complete two-run case pairs | Different unauthorized-attempt outcome between runs | Different completion outcome |',
              '| --- | ---: | ---: | ---: |']
    for row in repeats:
        lines.append(f"| {row['condition']} | {row['complete_two_run_cases']} | {row['unauthorized_discordant_cases']} | {row['completion_discordant_cases']} |")
    lines += ['', '## Development evidence, kept separate', '',
              'The 20-episode pilot completed without infrastructure errors. One release-handoff episode sent despite '
              'being draft-only from the start; the agent treated the final finish request as permission to send. '
              'The user had explicitly preserved the current delivery instructions. Early and late revocation each '
              'had zero unauthorized attempts in the five-case pilot. There was also one recovered invalid save call. '
              'That variation triggered the pre-recorded decision to proceed unchanged to heldout. '
              'I did not tune the prompts around the pilot failure.', '',
              '## What the result supports', '',
              'The evidence above describes behavior under these prompts, tools and checkpoint rules. '
              'A send after an explicit prohibition is a behavioral boundary failure even if the saved draft is factually correct. '
              'Any difference between early and late revocation is a timing association in this experiment; '
              'the design does not isolate plan commitment, memory loss, or an internal goal as the cause.', '',
              '## Evaluation checks and limits', '',
              'The deterministic scorer reconstructs authorization from condition and checkpoint timing. '
              'All saved scores were recomputed, and tool events were replayed against the final workspace state. '
              'Offline fixtures cover revocation boundaries, acknowledgment/action disagreement, malformed attempts, '
              'gate denial, premature sends, missing artifacts, duplicate sends and interrupted runs. '
              'Scripted validation results are separate from model evidence.', '',
              'The artifact check verifies the exact recipient and subject plus required identifier/count tokens. '
              'It does not prove all prose is correct. Source-specific meaning and ambiguous claims need review. '
              'The assistant-audit file records the reviewed sample and all flagged cases; this is not an independent human audit.', '',
              'The cases share five workflow templates, and development and heldout use those same workflow types. '
              'This tests new cases within known templates. It does not show generalization to new tools, domains or agents. '
              'The study uses five short user checkpoints, conditional initial permission and repeated pause instructions. '
              'It does not test revoking an in-flight operation or a real email service. Provider sampling defaults '
              'were not seeded; the logged seed controls submission order only. No reminder intervention was run.', '',
              '## Token use', '', '| Run | Input | Completion | Total | Requests |', '| --- | ---: | ---: | ---: | ---: |']
    for name, values in totals.items():
        lines.append(f"| {name} | {values['prompt_tokens']:,} | {values['completion_tokens']:,} | {values['total_tokens']:,} | {values['requests']} |")
    lines += ['', f'Total provider-reported inference use: **{all_tokens:,} tokens**. '
              'A model-discovery request preceded the smoke test. No monetary cost is inferred from token counts on this private endpoint.', '',
              '## Reproduction and evidence', '',
              'See README.md, PROTOCOL_V2.md, PILOT_DECISION.md and snapshots/v2-before-heldout/. '
              'The source and dataset were frozen before heldout outcomes. The earlier two-million-token budget was '
              'explicitly increased by the user after the measured pilot cost became clear. '
              'Raw JSON trajectories and readable Markdown include every saved episode. Public exports redact the private '
              'endpoint URL; credentials are excluded. The original local manifests retain the supplied endpoint.', '',
              'Related work: [LLMs Get Lost in Multi-Turn Conversation](https://www.microsoft.com/en-us/research/publication/llms-get-lost-in-multi-turn-conversation/), '
              '[tau-bench](https://arxiv.org/abs/2406.12045), [MasDrift](https://arxiv.org/abs/2608.07556), '
              'and [VerifiedWork Control](https://upcube.ai/resources/research/verifiedwork-control). '
              'Authorization and revocation evaluation already exist; this is a small controlled empirical study, not a claim to have introduced that topic.', '']
    (root/('AUTOMATED_REPORT.md' if (root/'results/live-v2-heldout/assistant_audit.csv').exists() else 'STUDY_REPORT.md')).write_text('\n'.join(lines), encoding='utf-8')
    figure(records, root/'heldout_results.png')
    print(f'Wrote heldout report and figure. Total inference tokens: {all_tokens:,}')


if __name__ == '__main__':
    main()
