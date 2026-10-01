from rest_framework.response import Response
from rest_framework.views import exception_handler

from core.client_disconnect import handle_cancelled_search_exception


def dap_exception_handler(exc, context):
    if handle_cancelled_search_exception(exc):
        return Response({'detail': 'Search cancelled.'}, status=499)
    return exception_handler(exc, context)
