"""Count final tests per subject and the distinct API request sequences they share.

Reads the compiled final suites (pytest-export-final/<case>/test_final_calibrated_suite.py) of the five
subjects, parses each test's `steps` literal and groups tests by their request sequence under three
definitions:
  A  exact: identical `steps` literal (same recorded request instances, settle policy, arms)
  B  sequence: same ordered (arm, actor, method, path, phase) of every http step plus reset/settle markers,
     ignoring which recorded request instance supplied the values   <- the definition reported in the paper
  C  method+path only: same ordered (method, path) of the http steps, ignoring actor and arm
Usage (repository root): python3 scripts/experiments/rq1_tools/count_api_sequences.py
"""
import ast, glob, json, collections
ROOTS = {
    'conduit': 'eval/ui_semantics/deepseek-full-20260912/conduit/pytest-export-final',
    'rwa': 'eval/ui_semantics/deepseek-full-20260912/rwa/pytest-export-final',
    'umami': 'eval/ui_semantics/umami-20260921/umami/pytest-export-final',
    'paperless': 'eval/ui_semantics/paperless-20260921/paperless/pytest-export-final',
    'ghost': 'eval/ui_semantics/ghost-20260921/ghost/pytest-export-final',
}
def key_b(steps):
    k = []
    for s in steps:
        kind = s.get('kind')
        if kind == 'http':
            k.append(('http', s.get('arm'), s.get('actor'), s.get('method'), s.get('path'), (s.get('phase') or '').split('[')[0]))
        elif kind == 'reset_and_authenticate':
            k.append(('reset', s.get('arm'), tuple(s.get('actors') or [])))
        elif kind == 'settle':
            k.append(('settle',))
        else:
            k.append((kind, s.get('arm')))
    return tuple(k)
def key_c(steps):
    return tuple((s.get('method'), s.get('path')) for s in steps if s.get('kind') == 'http')
def main():
    tot, ua, ub, uc, cases = (collections.Counter() for _ in range(5))
    for subj, root in ROOTS.items():
        for f in sorted(glob.glob(root + '/*/test_final_calibrated_suite.py')):
            tree = ast.parse(open(f).read()); ka, kb, kc, n = set(), set(), set(), 0
            for node in tree.body:
                if not (isinstance(node, ast.FunctionDef) and node.name.startswith('test_')):
                    continue
                steps = None
                for st in node.body:
                    if isinstance(st, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'steps' for t in st.targets):
                        steps = ast.literal_eval(st.value)
                if steps is None:
                    continue
                n += 1; ka.add(json.dumps(steps, sort_keys=True)); kb.add(key_b(steps)); kc.add(key_c(steps))
            tot[subj] += n; ua[subj] += len(ka); ub[subj] += len(kb); uc[subj] += len(kc); cases[subj] += 1 if n else 0
    print(f"{'subject':10s} {'cases':>5s} {'tests':>6s} {'A exact':>8s} {'B sequence':>11s} {'C method+path':>14s}")
    for s in ROOTS:
        print(f"{s:10s} {cases[s]:5d} {tot[s]:6d} {ua[s]:8d} {ub[s]:11d} {uc[s]:14d}")
    print(f"{'total':10s} {sum(cases.values()):5d} {sum(tot.values()):6d} {sum(ua.values()):8d} {sum(ub.values()):11d} {sum(uc.values()):14d}")
if __name__ == '__main__':
    main()
