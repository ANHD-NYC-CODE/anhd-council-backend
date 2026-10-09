"""One-shot script: add @unittest.skip decorators to the broken tests
identified by the 2026-06-15 test run.

Run: docker exec app python /app/scripts/mark_broken_tests.py
"""
import os
import re
import sys

BROKEN_TESTS = [
    # (relative path under anhd-council-backend, class_name, method_name)
    # All 2026-06-15 entries revived (2026-10-09) — see docs/TEST_SUITE_REVIVE.md.
]

SKIP_DECORATOR = '@unittest.skip("FIXME: broken fixture — see 2026-06-15 test sweep")'
SKIP_IMPORT = 'import unittest'


def patch_file(file_path, broken_methods_by_class):
    """Insert @unittest.skip above each broken test method in this file.
    `broken_methods_by_class` is dict {class_name: set(method_names)}."""
    with open(file_path) as f:
        source = f.read()

    # Ensure `import unittest` is present
    if 'import unittest' not in source:
        # Insert after any opening docstring + initial imports
        lines = source.splitlines(keepends=True)
        insert_at = 0
        for i, line in enumerate(lines):
            if line.startswith('from ') or line.startswith('import '):
                insert_at = i + 1
            elif insert_at > 0 and not line.strip():
                break
        lines.insert(insert_at, SKIP_IMPORT + '\n')
        source = ''.join(lines)

    # Track current class while iterating
    new_lines = []
    current_class = None
    skipped_count = 0
    for line in source.splitlines(keepends=True):
        # Detect class definition
        m_class = re.match(r'^class (\w+)', line)
        if m_class:
            current_class = m_class.group(1)
            new_lines.append(line)
            continue

        # Detect method definition inside a class we care about
        m_method = re.match(r'^(\s+)def (\w+)\(', line)
        if (m_method and current_class in broken_methods_by_class
                and m_method.group(2) in broken_methods_by_class[current_class]):
            indent = m_method.group(1)
            # Check if the prior non-empty line already has @unittest.skip
            prior_idx = len(new_lines) - 1
            while prior_idx >= 0 and not new_lines[prior_idx].strip():
                prior_idx -= 1
            if prior_idx >= 0 and 'unittest.skip' in new_lines[prior_idx]:
                new_lines.append(line)
                continue
            # Insert decorator with matching indent
            new_lines.append(f'{indent}{SKIP_DECORATOR}\n')
            skipped_count += 1
            new_lines.append(line)
            continue

        new_lines.append(line)

    with open(file_path, 'w') as f:
        f.write(''.join(new_lines))
    return skipped_count


def main():
    by_file = {}
    for path, cls, method in BROKEN_TESTS:
        by_file.setdefault(path, {}).setdefault(cls, set()).add(method)

    total = 0
    for path, classes in by_file.items():
        abs_path = os.path.join(os.path.dirname(__file__), '..', path)
        if not os.path.exists(abs_path):
            print(f'  SKIP (missing): {path}')
            continue
        n = patch_file(abs_path, classes)
        flat_count = sum(len(m) for m in classes.values())
        print(f'  {path}: added {n} decorators ({flat_count} expected)')
        total += n
    print(f'\nTotal decorators added: {total} (expected {len(BROKEN_TESTS)})')


if __name__ == '__main__':
    main()
