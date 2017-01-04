import sys
import logging
import traceback

from django.http import HttpResponse

logger = logging.getLogger(__name__)


def bad_request(request):
    type, value, tb = sys.exc_info()
    logger.error(traceback.format_exc())

    return HttpResponse('{{"Status":"ERROR",Message="{}"}}\n'.format(value), content_type="application/json",
                        status=400)


def permission_denied(request):
    tp, value, tb = sys.exc_info()
    logger.error(traceback.format_exc())

    return HttpResponse('{{"Status":"ERROR",Message="{}"}}\n'.format(value), content_type="application/json",
                        status=403)


def page_not_found(request):
    type, value, tb = sys.exc_info()
    logger.error(traceback.format_exc())

    return HttpResponse('{{"Status":"ERROR",Message="{}"}}\n'.format(value), content_type="application/json",
                        status=404)


def server_error(request):
    tp, value, tb = sys.exc_info()
    logger.error(traceback.format_exc())

    return HttpResponse('{{"Status":"ERROR",Message="{}"}}\n'.format(value), content_type="application/json",
                        status=500)


class Http400(Exception):
    pass


class Http500(Exception):
    pass


class ProcessExceptionMiddleware(object):
    def process_exception(self, request, exception):
        if isinstance(exception, Http400):
            return bad_request(request)
        if isinstance(exception, Http500):
            return server_error(request)

        logger.error(traceback.format_exc())

        return None
