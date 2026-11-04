"""Export the review package, excluding credentials and redacting private endpoint URLs."""
import hashlib
import json
from pathlib import Path
import zipfile

import experiment as e


def main():
    root = e.ROOT
    names = ['render_report.py', 'REVIEW_STATUS.md', 'STUDY_REPORT.pdf', 'FOLDER_REPORT.md', 'TRANSPORT_RECOVERY.md', 'README.md', 'STUDY_REPORT.md', 'STUDY_RESULTS.json', 'heldout_results.png',
             'PROTOCOL.md', 'PROTOCOL_V2.md', 'PILOT_DECISION.md', 'RESEARCH_NOTES.md',
             'SMOKE_TEST.md', 'VALIDATION.md', 'experiment.py', 'analyze.py', 'test_experiment.py',
             'study_dataset.py', 'report_study.py', 'package_study.py', 'scenarios.json',
             'scenarios_v2.json', 'AUDIT_TEMPLATE.csv', '.gitignore']
    entries = {name: (root/name).read_bytes() for name in names}
    for folder in ['snapshots', 'results/live-modal-smoke-v1', 'results/live-v2-pilot',
                   'results/live-v2-heldout', 'results/validation-compliant',
                   'results/validation-stale', 'results/validation-gate', 'results/validation-v2-parallel']:
        for path in (root/folder).rglob('*'):
            if not path.is_file() or path.name.startswith('.env') or '__pycache__' in path.parts:
                continue
            name = path.relative_to(root).as_posix()
            data = path.read_bytes()
            if path.name == 'manifest.json':
                manifest = json.loads(data)
                if manifest.get('evidence') == 'live_api':
                    manifest['config']['base_url'] = '<private endpoint redacted; use local .env>'
                    manifest['public_export_note'] = 'Only base_url redacted. Original local manifest preserved.'
                    data = (json.dumps(manifest, indent=2, ensure_ascii=False)+'\n').encode()
            entries[name] = data
    entries['.env.example'] = (b'# Keep real credentials in your private .env only.\n'
                               b'MODAL_CHADNI_PROXY_TOKEN_ID=""\n'
                               b'MODAL_CHADNI_PROXY_TOKEN_SECRET=""\n'
                               b'MODAL_CHADNI_ENDPOINT_URL=""\n')
    entries['CHECKSUMS.sha256'] = ''.join(hashlib.sha256(data).hexdigest()+'  '+name+'\n'
                                        for name, data in sorted(entries.items())).encode()
    # Inspect bytes in memory against credentials, without logging any credential values.
    e.load_env(root/'.env')
    import os
    secrets = [os.environ.get(k, '').encode() for k in ('MODAL_CHADNI_PROXY_TOKEN_ID',
               'MODAL_CHADNI_PROXY_TOKEN_SECRET', 'MODAL_CHADNI_ENDPOINT_URL', 'OPENAI_API_KEY')]
    if any(secret and secret in data for secret in secrets for data in entries.values()):
        raise ValueError('Private configuration detected in export; package was not written')
    archive = root/'Tess_Revocation_Experiment.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as output:
        for name, data in sorted(entries.items()):
            output.writestr(name, data)
    with zipfile.ZipFile(archive) as output:
        if output.testzip() is not None or '.env' in output.namelist():
            raise ValueError('Package verification failed')
    print(f'Verified {len(entries)} exported files. Credentials and endpoint URL excluded.')


if __name__ == '__main__':
    main()
