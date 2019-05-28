from decimal import Decimal
from .models import TypeTask, Task, Ecm, TypeTaskMain, TaskStatus, TaskFilterViewModel
from .serializers import TypeTaskSerializer, TaskSerializer, TaskCreateSerializer, EcmTaskSerializer, \
    TypeTaskMainSerializer, CustomResultsSetPagination, TaskDashboardSerializer, TaskToPayDashboardSerializer, \
    LargeResultsSetPagination, TotalToPayByOfficeSerializer
from .filters import TaskApiFilter, TypeTaskMainFilter, TaskDashboardApiFilter
from .utils import filter_api_queryset_by_params
from rest_framework import viewsets, mixins
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope
from rest_framework.decorators import permission_classes
from core.views_api import ApplicationView
from lawsuit.models import Folder
from django.utils import timezone
from django.db.models import Q, Sum
from core.views_api import OfficeMixinViewSet


@permission_classes((TokenHasReadWriteScope,))
class TypeTaskMainViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TypeTaskMain.objects.all()
    serializer_class = TypeTaskMainSerializer
    filter_backends = (SearchFilter, DjangoFilterBackend)
    filter_class = TypeTaskMainFilter
    search_fields = ('name', )


@permission_classes((TokenHasReadWriteScope, ))
class TypeTaskViewSet(OfficeMixinViewSet):
    queryset = TypeTask.objects.filter(is_active=True)
    serializer_class = TypeTaskSerializer
    filter_backends = (SearchFilter, )
    search_fields = ('name', 'legacy_code')


@permission_classes((TokenHasReadWriteScope, ))
class EcmTaskViewSet(mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet,
                     ApplicationView):
    queryset = Ecm.objects.all()
    serializer_class = EcmTaskSerializer

    def get_queryset(self, *args, **kwargs):
        office = self.request.auth.application.office
        return self.queryset.filter(Q(tasks__office=office.id) | Q(task__office_id=office.id)).distinct()


@permission_classes((TokenHasReadWriteScope, ))
class TaskViewSet(OfficeMixinViewSet, ApplicationView):
    filter_backends = (DjangoFilterBackend, OrderingFilter, )
    filter_class = TaskApiFilter
    pagination_class = CustomResultsSetPagination
    ordering_fields = ('id', 'create_date', 'final_deadline_date', 'office_name', 'task_number', 'type_task_name',
                       'amount', 'lawsuit_number', 'state', 'court_district_name', 'task_status')
    default_ordering = ('-final_deadline_date', )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return TaskCreateSerializer
        return TaskSerializer

    def get_queryset(self):
        self.queryset = Task.objects.all()
        queryset = super().get_queryset()
        params = self.request.query_params
        return filter_api_queryset_by_params(queryset, params)


@permission_classes((TokenHasReadWriteScope, ))
class TaskDashboardEZLViewSet(OfficeMixinViewSet, ApplicationView):
    serializer_class = TaskDashboardSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter,)
    filter_class = TaskDashboardApiFilter
    pagination_class = CustomResultsSetPagination
    ordering_fields = ('id', 'create_date', 'final_deadline_date', 'office_name', 'task_number', 'type_task_name',
                       'amount', 'lawsuit_number', 'state_initials', 'court_district_name', 'task_status',
                       'asked_by_legal_name', 'executed_by_legal_name', 'task_hash')
    default_ordering = ('-final_deadline_date',)

    def get_queryset(self):
        queryset = TaskFilterViewModel.objects.all()
        if not self.request.query_params.get('parent_id'):
            queryset = TaskFilterViewModel.objects.filter(
                Q(parent__isnull=True),
                Q(office__customsettings__show_task_in_admin_dash=True))

            params = self.request.query_params
            queryset = filter_api_queryset_by_params(queryset, params)
        return queryset.distinct()


@api_view(['GET'])
@permission_classes((TokenHasReadWriteScope, ))
def list_audience_totals(request):
    company = request.auth.application.company
    audience = {}
    if company.users.filter(user=request.user).exists():
        folders = Folder.objects.filter(person_customer__company=company)
        tasks = Task.objects.filter(movement__folder__in=folders)
        audiences = tasks.filter(type_task__is_audience=True)
        audiences_this_month = audiences.filter(
            final_deadline_date__year=timezone.now().year,
            final_deadline_date__month=timezone.now().month)
        agreement_this_month = audiences_this_month.filter(
            **{'survey_result__Acordo realizado?': 'Sim'})
        audiences_this_week = audiences_this_month.filter(
            final_deadline_date__week=timezone.now().isocalendar()[1])
        audience['total_audience'] = audiences.count()
        audience['total_audience_this_month'] = audiences_this_month.count()
        audience['total_audience_this_week'] = audiences_this_week.count()
        audience['agreement_this_month'] = agreement_this_month.count()
    return Response(audience)


@permission_classes((TokenHasReadWriteScope, ))
class TotalToPayByOfficeViewSet(viewsets.ReadOnlyModelViewSet, ApplicationView):
    serializer_class = TotalToPayByOfficeSerializer
    pagination_class = LargeResultsSetPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter,)
    filter_class = TaskApiFilter

    def get_queryset(self):
        queryset = Task.objects\
            .select_related('office')\
            .filter(task_status=TaskStatus.FINISHED,
                    parent__isnull=True,
                    amount_to_pay__gt=Decimal('0.00'))
        params = self.request.query_params
        queryset = filter_api_queryset_by_params(queryset, params)

        return queryset.order_by('office__legal_name')\
            .values('office_id', 'office__legal_name')\
            .annotate(total_to_pay=Sum('amount_to_pay'), total_delegated=Sum('amount_delegated'))


@permission_classes((TokenHasReadWriteScope, ))
class TaskToPayViewSet(viewsets.ReadOnlyModelViewSet, ApplicationView):
    serializer_class = TaskToPayDashboardSerializer
    pagination_class = CustomResultsSetPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter,)
    filter_class = TaskApiFilter

    def get_queryset(self):
        queryset = Task.objects \
            .select_related('office') \
            .select_related('type_task') \
            .select_related('movement__type_movement') \
            .select_related('movement__folder') \
            .select_related('movement__folder__person_customer') \
            .select_related('movement__folder__cost_center') \
            .select_related('movement__law_suit') \
            .select_related('movement__law_suit__court_district') \
            .select_related('parent__type_task') \
            .filter(task_status=TaskStatus.FINISHED,
                    parent__isnull=True,
                    amount_to_pay__gt=Decimal('0.00')) \
            .order_by('office_id', '-finished_date')
        params = self.request.query_params
        queryset = filter_api_queryset_by_params(queryset, params)
        return queryset


@permission_classes((TokenHasReadWriteScope, ))
class ChildTaskToPayViewSet(viewsets.ReadOnlyModelViewSet, ApplicationView):
    serializer_class = TaskToPayDashboardSerializer
    pagination_class = CustomResultsSetPagination

    def get_queryset(self):
        queryset = Task.objects.none()
        parent_id = self.request.query_params.get('parent_id')
        if parent_id:
            id_list = []
            task = Task.objects.get(pk=parent_id)
            while task.get_child:
                id_list.append(task.get_child.id)
                task = task.get_child

            queryset = Task.objects \
                .select_related('office') \
                .select_related('type_task') \
                .select_related('movement__type_movement') \
                .select_related('movement__folder') \
                .select_related('movement__folder__person_customer') \
                .select_related('movement__law_suit__court_district') \
                .select_related('parent__type_task') \
                .filter(id__in=id_list) \
                .order_by('office_id', 'finished_date')
        return queryset

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset)
