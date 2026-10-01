import logging
import select
import socket
import threading
from contextlib import contextmanager

from django.db import connections
from django.db.utils import DatabaseError, OperationalError

logger = logging.getLogger('app')


def is_custom_search_properties_request(request):
    """Long-running portal custom search JSON (AbortController target)."""
    if '/properties/' not in request.path:
        return False
    qp = request.GET
    return (
        qp.get('summary') == 'true'
        and qp.get('summary-type', '').lower() == 'custom-search'
        and qp.get('format') == 'json'
    )


def query_was_cancelled(exc):
    msg = str(exc).lower()
    return 'canceling statement' in msg or 'query canceled' in msg


def cancel_all_db_connections():
    for conn in connections.all(initialized_only=True):
        try:
            conn.cancel()
        except Exception as exc:
            logger.debug('connection.cancel() failed: %s', exc)


def request_client_socket(request):
    """Best-effort socket for the active WSGI request (gunicorn)."""
    environ = request.META
    sock = environ.get('gunicorn.socket')
    if sock is not None:
        return sock
    wsgi_input = environ.get('wsgi.input')
    if wsgi_input is None:
        return None
    for attr in ('socket', '_sock'):
        candidate = getattr(wsgi_input, attr, None)
        if candidate is not None:
            return candidate
    return None


class ClientDisconnectWatcher:
    """Poll the client socket; cancel Postgres if the browser closes the connection."""

    def __init__(self, sock):
        self._sock = sock
        self._stop = threading.Event()
        self._thread = None

    def start(self):
        self._thread = threading.Thread(
            target=self._run,
            name='custom-search-disconnect',
            daemon=True,
        )
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=1.0)

    def _run(self):
        sock = self._sock
        while not self._stop.is_set():
            try:
                readable, _, _ = select.select([sock], [], [], 0.5)
                if not readable:
                    continue
                try:
                    peek = sock.recv(1, socket.MSG_PEEK | socket.MSG_DONTWAIT)
                except BlockingIOError:
                    continue
                if peek == b'':
                    logger.info('Custom search client disconnected; cancelling DB work')
                    cancel_all_db_connections()
                    break
            except OSError as exc:
                if not self._stop.is_set():
                    logger.info(
                        'Custom search client disconnected (%s); cancelling DB work',
                        exc,
                    )
                    cancel_all_db_connections()
                break


@contextmanager
def client_disconnect_guard(request):
    if not is_custom_search_properties_request(request):
        yield
        return

    sock = request_client_socket(request)
    if sock is None:
        yield
        return

    watcher = ClientDisconnectWatcher(sock)
    watcher.start()
    try:
        yield
    finally:
        watcher.stop()


def handle_cancelled_search_exception(exc):
    return isinstance(exc, (OperationalError, DatabaseError)) and query_was_cancelled(exc)
