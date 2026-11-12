from django.http import JsonResponse
from django.views.decorators.http import require_GET

from core.celery_health import evaluate_celery_heartbeat


@require_GET
def celery_health_view(request):
    status = evaluate_celery_heartbeat()
    http_status = 200 if status['ok'] else 503
    return JsonResponse(status, status=http_status)
