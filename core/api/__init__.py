from django.http import JsonResponse
from django.views import View


class ApiError(BaseException):

    status_code = None


class BadRequestError(ApiError):
    status_code = 400


class ApiViewMixin(View):

    model = None

    def get_queryset(self):
        return self.model.objects.filter(is_active=True)

    def filter_queryset(self, queryset):
        return queryset

    def get(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
        except ApiError as exc:
            return JsonResponse({"error": exc.args[0]}, status=exc.status_code)

        items = [x.serialize() for x in queryset] if queryset.exists() else []
        return JsonResponse({"data": items})

    def bad_request(self, message):
        raise BadRequestError(message)
