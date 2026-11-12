"""Async custom-search job endpoints.

POST   /properties/custom-search/jobs/             {"path": "/councils/1/properties/", "params": {...}}
GET    /properties/custom-search/jobs/<uuid>/      -> status / percent / phase / results | refetch
DELETE /properties/custom-search/jobs/<uuid>/      -> cancel (best effort; a running query finishes)

Anonymous access mirrors the public /properties/ list. Protected-dataset
access is enforced here because the worker queries the origin as trusted.
"""

from django.http import QueryDict
from django.test import RequestFactory
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from core.custom_search_jobs import create_custom_search_job, get_job_state, set_job_state
from core.custom_search_policy import (
    is_any_custom_search_json_list,
    is_blocked_borough_unfiltered_custom_search,
    is_blocked_citywide_custom_search,
    is_valid_custom_search_path,
    q_references_protected_dataset,
)
from datasets.helpers.cache_helpers import is_authenticated, scrub_authenticated
from datasets.views.property_views import (
    BOROUGH_CUSTOM_SEARCH_BLOCKED_DETAIL,
    CITYWIDE_CUSTOM_SEARCH_BLOCKED_DETAIL,
)

PROTECTED_LOGIN_DETAIL = 'Please login and request access to view results'


def _flatten(params):
    """QueryDict / dict-of-lists -> dict of scalars (last value wins)."""
    if isinstance(params, QueryDict):
        return params.dict()
    flat = {}
    for key, value in (params or {}).items():
        if isinstance(value, (list, tuple)):
            value = value[-1] if value else ''
        flat[key] = value
    return flat


def _parse_start_body(request):
    data = request.data
    if isinstance(data, dict) and 'params' in data and isinstance(data.get('params'), dict):
        return data.get('path') or '/properties/', _flatten(data['params'])
    if data:
        params = _flatten(data)
        return params.pop('path', None) or '/properties/', params
    params = _flatten(request.query_params)
    return params.pop('path', None) or '/properties/', params


@api_view(['POST'])
@permission_classes([AllowAny])
def start_custom_search_job(request):
    path, query_params = _parse_start_body(request)
    query_params['format'] = 'json'

    if not is_valid_custom_search_path(path):
        return Response({'detail': 'Invalid custom search path.'}, status=status.HTTP_400_BAD_REQUEST)

    synthetic = RequestFactory().get(path, query_params)
    if not is_any_custom_search_json_list(synthetic):
        return Response({'detail': 'Invalid custom search request.'}, status=status.HTTP_400_BAD_REQUEST)
    if is_blocked_citywide_custom_search(synthetic):
        return Response({'detail': CITYWIDE_CUSTOM_SEARCH_BLOCKED_DETAIL}, status=status.HTTP_400_BAD_REQUEST)
    if is_blocked_borough_unfiltered_custom_search(synthetic):
        return Response({'detail': BOROUGH_CUSTOM_SEARCH_BLOCKED_DETAIL}, status=status.HTTP_400_BAD_REQUEST)
    if q_references_protected_dataset(query_params.get('q')) and not is_authenticated(request):
        return Response({'detail': PROTECTED_LOGIN_DETAIL}, status=status.HTTP_401_UNAUTHORIZED)

    job_id = create_custom_search_job(path, query_params)
    return Response({'job_id': job_id, 'status': 'queued', 'percent': 0}, status=status.HTTP_202_ACCEPTED)


@api_view(['GET', 'DELETE'])
@permission_classes([AllowAny])
def poll_custom_search_job(request, job_id):
    job_id = str(job_id)
    state = get_job_state(job_id)
    if not state:
        return Response({'detail': 'Job not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        if state.get('status') not in ('complete', 'failed'):
            state = set_job_state(job_id, status='cancelled', phase='cancelled')
        return Response({'job_id': job_id, 'status': state.get('status')})

    payload = {
        'job_id': job_id,
        'status': state.get('status'),
        'percent': state.get('percent', 0),
        'phase': state.get('phase'),
        'http_status': state.get('http_status'),
        'error': state.get('error'),
    }
    if state.get('status') == 'complete':
        result = state.get('result')
        if result is not None:
            result = scrub_authenticated(result, request)
            payload['results'] = result
            payload['result_count'] = len(result) if isinstance(result, list) else None
        else:
            payload['refetch'] = True
            payload['path'] = state.get('path') or '/properties/'
            payload['query_params'] = state.get('query_params')
    return Response(payload)
