from django.utils.deprecation import MiddlewareMixin
from django.conf import settings


class ReviewRequestMiddleware(MiddlewareMixin):
    """
    Retorna a revisao atual do repositorio
    """

    def process_request(self, request):
        request.REVIEW = settings.REVIEW
