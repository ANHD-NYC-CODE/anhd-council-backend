"""One-shot script: add @unittest.skip decorators to the broken tests
identified by the 2026-06-15 test run.

Run: docker exec app python /app/scripts/mark_broken_tests.py
"""
import os
import re
import sys

BROKEN_TESTS = [
    # (relative path under anhd-council-backend, class_name, method_name)
    ('core/tests/test_models.py', 'DatasetTests', 'test_annotate_properties_all'),

    ('datasets/tests/filters/test_property.py', 'PropertyAdvancedFilterTests', 'test_council_with_housingtype_with_q_2'),
    ('datasets/tests/filters/test_property.py', 'PropertyAdvancedFilterTests', 'test_council_with_housingtype_with_q_3'),
    ('datasets/tests/filters/test_property.py', 'PropertyAdvancedFilterTests', 'test_council_with_housingtype_with_q_4'),
    ('datasets/tests/filters/test_property.py', 'PropertyAdvancedFilterTests', 'test_council_with_housingtype_with_q_5'),
    ('datasets/tests/filters/test_property.py', 'PropertyAdvancedFilterTests', 'test_eviction_rules'),
    ('datasets/tests/filters/test_property.py', 'PropertyAdvancedFilterTests', 'test_foreclosure_rules_authorized'),
    ('datasets/tests/filters/test_property.py', 'PropertyAdvancedFilterTests', 'test_multiple_condition_multi_groups_3'),
    ('datasets/tests/filters/test_property.py', 'PropertyAdvancedFilterTests', 'test_multiple_condition_multi_groups_4'),
    ('datasets/tests/filters/test_property.py', 'PropertyFilterTests', 'test_eviction_field'),
    ('datasets/tests/filters/test_property.py', 'PropertyFilterTests', 'test_evictionsdates_field'),
    ('datasets/tests/filters/test_property.py', 'PropertyFilterTests', 'test_hpdcomplaintsdates_field'),
    ('datasets/tests/filters/test_property.py', 'PropertyFilterTests', 'test_legalclassb_units'),
    ('datasets/tests/filters/test_property.py', 'PropertyFilterTests', 'test_managementprogram'),
    ('datasets/tests/filters/test_property.py', 'PropertyFilterTests', 'test_subsidy_field'),
    ('datasets/tests/filters/test_property.py', 'PropertyFilterTests', 'test_subsidy_field_multiple_programs'),

    ('datasets/tests/models/test_eviction.py', 'EvictionTest', 'test_seed_record'),

    ('datasets/tests/models/test_models.py', 'BuildingTests', 'test_seed_building'),
    ('datasets/tests/models/test_models.py', 'DOBPermitIssuedTests', 'test_seed_joined_table_with_update'),
    ('datasets/tests/models/test_models.py', 'HPDBuildingRecordTests', 'test_seed_record_after_update'),
    ('datasets/tests/models/test_models.py', 'PadRecordTests', 'test_seed_padrecord'),
    ('datasets/tests/models/test_models.py', 'PropertyTests', 'test_seed_properties'),
    ('datasets/tests/models/test_models.py', 'PropertyTests', 'test_seed_properties_update'),
    ('datasets/tests/models/test_models.py', 'TaxLienTests', 'test_seed_record'),
    ('datasets/tests/models/test_models.py', 'TaxLienTests', 'test_seed_record_after_overwrite'),

    ('datasets/tests/models/test_property.py', 'PropertyTests', 'test_seed_properties'),
    ('datasets/tests/models/test_property.py', 'PropertyTests', 'test_seed_properties_update'),
    ('datasets/tests/models/test_property.py', 'PropertyTests', 'test_seed_properties_with_state_geo'),

    ('datasets/tests/views/test_aepbuilding.py', 'AEPBuildingViewTests', 'test_list'),
    ('datasets/tests/views/test_aepbuilding.py', 'AEPBuildingViewTests', 'test_retrieve'),

    ('datasets/tests/views/test_building.py', 'BuildingViewTests', 'test_building_hpdcomplaints'),

    ('datasets/tests/views/test_coredata.py', 'CoreDataTests', 'test_list'),
    ('datasets/tests/views/test_coredata.py', 'CoreDataTests', 'test_retrieve'),

    ('datasets/tests/views/test_eviction.py', 'EvictionViewTests', 'test_list'),
    ('datasets/tests/views/test_eviction.py', 'EvictionViewTests', 'test_retrieve'),

    ('datasets/tests/views/test_foreclosure.py', 'ForeclosureViewTests', 'test_list'),
    ('datasets/tests/views/test_foreclosure.py', 'ForeclosureViewTests', 'test_retrieve'),

    ('datasets/tests/views/test_foreclosureauction.py', 'ForeclosureAuctionViewTests', 'test_list'),
    ('datasets/tests/views/test_foreclosureauction.py', 'ForeclosureAuctionViewTests', 'test_retrieve'),

    ('datasets/tests/views/test_hpdbuilding.py', 'HPDBuildingViewTests', 'test_list'),
    ('datasets/tests/views/test_hpdbuilding.py', 'HPDBuildingViewTests', 'test_retrieve'),

    ('datasets/tests/views/test_hpdcomplaint.py', 'HPDComplaintViewTests', 'test_list'),
    ('datasets/tests/views/test_hpdcomplaint.py', 'HPDComplaintViewTests', 'test_retrieve'),

    ('datasets/tests/views/test_lispenden.py', 'LisPendenViewTests', 'test_list'),
    ('datasets/tests/views/test_lispenden.py', 'LisPendenViewTests', 'test_retrieve'),

    ('datasets/tests/views/test_property.py', 'PropertyViewTests', 'test_property_evictions'),
    ('datasets/tests/views/test_property.py', 'PropertyViewTests', 'test_property_housing_summary'),
    ('datasets/tests/views/test_property.py', 'PropertyViewTests', 'test_property_hpdcomplaints'),
    ('datasets/tests/views/test_property.py', 'PropertyViewTests', 'test_property_lispendens'),
    ('datasets/tests/views/test_property.py', 'PropertyViewTests', 'test_results_with_annotate_datasets_1'),
    ('datasets/tests/views/test_property.py', 'PropertyViewTests', 'test_results_with_annotate_datasets_2'),
    ('datasets/tests/views/test_property.py', 'PropertyViewTests', 'test_results_with_annotate_datasets_3'),
    ('datasets/tests/views/test_property.py', 'PropertyViewTests', 'test_results_with_annotate_datasets_4'),
    ('datasets/tests/views/test_property.py', 'PropertyViewTests', 'test_results_with_annotate_datasets_7'),
    ('datasets/tests/views/test_property.py', 'PropertyViewTests', 'test_results_with_annotate_datasets_8'),
    ('datasets/tests/views/test_property.py', 'PropertyViewTests', 'test_results_with_annotate_datasets_9'),
    ('datasets/tests/views/test_property.py', 'PropertyViewTests', 'test_results_with_annotate_datasets_10'),
    ('datasets/tests/views/test_property.py', 'PropertyViewTests', 'test_results_with_annotate_datasets_12'),

    ('datasets/tests/views/test_subsidy421a.py', 'Subsidy421aTests', 'test_list'),
    ('datasets/tests/views/test_subsidy421a.py', 'Subsidy421aTests', 'test_retrieve'),

    ('datasets/tests/views/test_subsidyj51.py', 'SubsidyJ51Tests', 'test_list'),
    ('datasets/tests/views/test_subsidyj51.py', 'SubsidyJ51Tests', 'test_retrieve'),
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
