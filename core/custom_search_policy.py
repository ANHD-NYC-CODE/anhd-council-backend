"""Custom-search request policy helpers."""

import re

# Query params that scope a /properties/ request to a district (see
# AdvancedPropertyFilter / PropertyFilter). Any of these means "not citywide".
DISTRICT_QUERY_PARAMS = ('council', 'community', 'stateassembly', 'statesenate', 'zipcode')

# Paths a custom search may target: borough/citywide on /properties/, or a
# nested district route (fe_to_be_url in datasets/utils/advanced_filter.py).
CUSTOM_SEARCH_PATH_RE = re.compile(
    r'^/(?:(?:councils|communities|stateassemblies|statesenates|zipcodes)/\d+/)?properties/$'
)

PROTECTED_Q_TERMS = ('lispenden', 'foreclosure', 'ocahousingcourt')


def _query_params(request):
    return getattr(request, 'query_params', request.GET)


# CSV export of a search re-runs the same (uncached) query, so it gets the same
# policy and concurrency limit as JSON.
GUARDED_FORMATS = ('json', 'csv')


def _is_custom_search_summary(qp):
    return (
        qp.get('summary') == 'true'
        and (qp.get('format') or 'json') in GUARDED_FORMATS
        and qp.get('summary-type', '').lower() == 'custom-search'
    )


def is_valid_custom_search_path(path):
    return bool(CUSTOM_SEARCH_PATH_RE.match(path or ''))


def is_custom_search_json_list(request):
    """Custom-search summary on the top-level /properties/ route (borough/citywide)."""
    if request.path != '/properties/':
        return False
    return _is_custom_search_summary(_query_params(request))


def is_any_custom_search_json_list(request):
    """Custom-search summary on /properties/ or a nested district properties route."""
    if not is_valid_custom_search_path(request.path):
        return False
    return _is_custom_search_summary(_query_params(request))


def q_references_protected_dataset(q):
    q = str(q or '')
    return any(term in q for term in PROTECTED_Q_TERMS)


# A real dataset filter looks like `filter_0=hpdviolations__count__gte=5`.
DATASET_FILTER_RE = re.compile(r'filter_\d+=[a-z0-9]+__[a-z0-9_]+')


def _q_has_dataset_filters(q):
    if not q or not str(q).strip():
        return False
    return bool(DATASET_FILTER_RE.search(str(q).lower()))


def is_citywide_custom_search_list(request):
    if not is_custom_search_json_list(request):
        return False
    qp = _query_params(request)
    if qp.get('borough'):
        return False
    if any(qp.get(param) for param in DISTRICT_QUERY_PARAMS):
        return False
    return True


def is_blocked_citywide_custom_search(request):
    return is_citywide_custom_search_list(request)


def is_blocked_borough_unfiltered_custom_search(request):
    """Borough + housingtype=all + no dataset filters in q."""
    if not is_custom_search_json_list(request):
        return False
    qp = _query_params(request)
    borough = qp.get('borough')
    if not borough:
        return False
    housing = (qp.get('housingtype') or 'all').strip().lower()
    if housing != 'all':
        return False
    if _q_has_dataset_filters(qp.get('q')):
        return False
    return True
