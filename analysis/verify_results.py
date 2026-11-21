"""Recalculate the experiment results and verify the saved datasets.

Uses Python's standard library only. No API requests are made.
"""
import csv
import hashlib
import importlib.util
import io
import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = [ROOT / 'experiment_01_initial', ROOT / 'experiment_02_diagnostic']
EXPECTED_SHA = [
    '0bcbbc2ace840f03bc405a72dd58b86064caccd6c17090e11fcefe207b532743',
    '295c7bf039a4f99ea3e1bcdb5cde2dba61cde2a5ed06daad9039f5f1d0e5cc96',
]
EXPECTED_SOURCE_SHA = [
    '10ccf01f71ac3d4fb5876631f3af79d743a2b729c9320d6549e62f52165374e8',
    'ac8282d10b7588b2f091a256db9b3d5c9b0d03e023883dd337a6c6f7f8413112',
]

def read_csv(path):
    with path.open('r', newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def key(row):
    return row['model'], row['case'], row['style'], row['run']

def load_experiment(path, i):
    spec = importlib.util.spec_from_file_location(f'experiment_check_{i}', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def verify():
    modules = []
    datasets = []
    for i, folder in enumerate(EXPERIMENTS):
        src = folder / 'experiment.py'
        data = folder / 'actual_run/results.csv'
        assert digest(data) == EXPECTED_SHA[i], f'Historical run {i+1} CSV changed'
        assert digest(src) == EXPECTED_SOURCE_SHA[i], f'Historical run {i+1} Python source changed'
        rows = read_csv(data)
        assert len(rows) == 150 and len({key(row) for row in rows}) == 150
        assert all(row['simulated'].strip().lower() == 'false' for row in rows)
        assert all(not row['error'].strip() for row in rows), 'There were unexpected API-error records'
        module = load_experiment(src, i)
        modules.append(module)
        datasets.append(rows)
        case_map = {c['id']: c for c in module.TEST_CASES}
        assert len(case_map) == 5 and len(module.STYLES) == 5
        assert len({r['model'] for r in rows}) == 2
        assert all(Counter((r['model'], r['case'], r['style']) for r in rows).get((model, case, style)) == 3
                   for model in {r['model'] for r in rows} for case in case_map for style in module.STYLES)
        for row in rows:
            case = case_map[row['case']]
            assert row['question'] == case['phrasings'][row['style']]
            assert math.isclose(float(row['golden']),round(case['golden'],6),abs_tol=1e-9)
            assert math.isclose(float(row['hint_value']),float(case['hint_value']),abs_tol=1e-9)
            assert math.isclose(float(row['tolerance']),float(case['tolerance']),abs_tol=1e-9)
            parsed = module.read_answer(row['raw_response'])
            expected = module.check_answer(parsed,case,row['style'])
            assert expected == row['status'], (i+1,key(row),expected,row['status'])
            if parsed is None:
                assert row['model_answer'] == '' and row['difference'] == ''
            else:
                assert math.isclose(float(row['model_answer']),parsed,abs_tol=1e-8)
                assert math.isclose(float(row['difference']),round(parsed-case['golden'],6),abs_tol=1e-8)
        statuses = Counter(row['status'] for row in rows)
        expected_counts = ({'MATCH':131,'NO_ANSWER':19} if i==0 else {'MATCH':150})
        assert dict(statuses) == expected_counts, (i, statuses)
        expected_model_counts = (
            {('claude-haiku-5-5','MATCH'):60,('claude-haiku-5-5','NO_ANSWER'):15,
             ('claude-sonnet-5-5','MATCH'):71,('claude-sonnet-5-5','NO_ANSWER'):4}
            if i==0 else {('claude-haiku-5-5','MATCH'):75,('claude-sonnet-5-5','MATCH'):75}
        )
        assert dict(Counter((r['model'],r['status']) for r in rows))==expected_model_counts
        report = (folder/'actual_run/results.md').read_bytes()
        assert report.decode('utf-8').replace('\r\n','\n') == (folder/'actual_run/summary.txt').read_text(encoding='utf-8').replace('\r\n','\n'), 'Original reports disagree beyond line ending differences'
        print(f'Run {i+1}: {len(rows)} genuine requests, {dict(statuses)}, source and results match recorded fingerprints')

    assert modules[0].PROMPT == modules[1].PROMPT, 'System prompts differ'
    assert modules[0].TEST_CASES == modules[1].TEST_CASES, 'Financial test cases differ'
    assert modules[0].STYLES == modules[1].STYLES, 'Question styles differ'
    idx1 = {key(r):r for r in datasets[0]}
    idx2 = {key(r):r for r in datasets[1]}
    assert set(idx1) == set(idx2)
    for k in idx1:
        for fld in ('question','golden','hint_value','tolerance'):
            assert idx1[k][fld] == idx2[k][fld], (k,fld)
    missing = [r for r in datasets[0] if r['status'] == 'NO_ANSWER']
    assert len(missing)==19
    assert sum(not r['raw_response'].strip() for r in missing)==6
    assert Counter(r['case'] for r in missing)=={'mortgage_payment':12,'bond_price':5,'annualized_return':2}
    assert Counter(r['style'] for r in missing)=={'misleading':7,'wordy':6,'direct':3,'embedded':3}
    assert all(idx2[key(row)]['status'] == 'MATCH' for row in missing)
    assert all(row['stop_reason'] == 'end_turn' for row in datasets[1])
    assert sum(int(r['output_tokens'])>1000 for r in datasets[1])==19
    assert sum(int(idx2[key(r)]['output_tokens'])>1000 for r in missing)==11
    assert Counter(r['content_types'] for r in datasets[1])=={'thinking,text':132,'text':18}
    pairs = read_csv(ROOT/'analysis/paired_runs.csv')
    assert len(pairs)==150 and len({key(r) for r in pairs})==150
    assert set(key(r) for r in pairs)==set(idx1)
    for pair in pairs:
        k=key(pair)
        assert pair['run1_status']==idx1[k]['status']
        assert pair['run2_status']==idx2[k]['status']
        assert pair['run1_answer']==idx1[k]['model_answer']
        assert pair['run2_answer']==idx2[k]['model_answer']
        assert pair['run2_output_tokens']==idx2[k]['output_tokens']
        assert pair['run2_stop_reason']==idx2[k]['stop_reason']
    # Manually inspected first-run records that explicitly state a correct number,
    # despite lacking a valid FINAL line. This is documented interpretation,
    # deliberately not an automatic reclassification.
    manually_observed = [
        ('claude-haiku-5-5','mortgage_payment','direct','2'),
        ('claude-sonnet-5-5','mortgage_payment','misleading','3'),
        ('claude-haiku-5-5','mortgage_payment','direct','3'),
        ('claude-haiku-5-5','bond_price','embedded','1'),
        ('claude-haiku-5-5','bond_price','misleading','2'),
        ('claude-sonnet-5-5','bond_price','misleading','2'),
    ]
    assert all(idx1[k]['status']=='NO_ANSWER' and idx1[k]['raw_response'].strip() for k in manually_observed)
    assert len(manually_observed)==6
    print('First-run unparsed: 19 total, 6 empty text; 6 separately inspected records visibly contain a correct value')
    print('Paired tasks: 150; all previous 19 NO_ANSWER records have MATCH in second run')
    print('Second-run output usage: 19 of 150 above 1,000 tokens, including 11 of 19 earlier NO_ANSWER task IDs')
    print('Second-run content types: 132 thinking,text and 18 text; 150 normal end_turn stops')
    # Checksums of every file except the manifest itself.
    manifest = ROOT/'MANIFEST_SHA256.txt'
    lines = manifest.read_text(encoding='utf-8').splitlines()
    hashes = {}
    for line in lines:
        if not line.strip() or line.startswith('#'):continue
        h, name = line.split('  ',1)
        hashes[name] = h
        path=ROOT/name
        assert path.exists() and digest(path)==h, f'Checksum mismatch: {name}'
    listed = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and p != manifest and '__pycache__' not in p.parts}
    assert set(hashes)==listed, ('Manifest coverage mismatch',sorted(listed-set(hashes)),sorted(set(hashes)-listed))
    print(f'Manifest: all {len(hashes)} distributed files verified')
    return True

if __name__=='__main__':
    verify()
    print('PASS: datasets, source, calculations, classifications, reports, paired data, and checksums')
