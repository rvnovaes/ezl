from django.db.models import Q
from django_filters import FilterSet
from .models import ServicePriceTable, CategoryPrice


class ServicePriceTableFilter(FilterSet):

    class Meta:
        model = ServicePriceTable
        fields = '__all__'

    def get_delegation_queryset(self):
        return self.queryset.filter(is_active=True)


class ServicePriceTableOfficeFilter(ServicePriceTableFilter):

    def get_delegation_queryset(self):
        qs = super().get_delegation_queryset()
        dynamic_query = Q()
        task = self.data.get('task')
        network_office_id_list = self.data.get('network_office_id_list')
        offices_related = self.data.get('offices_related')
        if task and network_office_id_list and offices_related:
            dynamic_query.add(
                Q(
                    Q(office=task.office) |
                    Q(
                        Q(policy_price__category=CategoryPrice.PUBLIC), ~Q(office=task.office)
                    ) |
                    Q(office_id__in=network_office_id_list)
                ), Q.AND)
            dynamic_query.add(
                Q(
                    Q(office_correspondent__in=offices_related) |
                    Q(
                        Q(policy_price__category=CategoryPrice.PUBLIC), ~Q(office_correspondent=task.office)
                    ) |
                    Q(office_correspondent__in=network_office_id_list)
                ), Q.AND)
            dynamic_query.add(
                Q(
                    Q(office_correspondent__is_active=True) | Q(office_correspondent__isnull=True)
                ), Q.AND
            )
        return qs.filter(dynamic_query)


class ServicePriceTableTypeTaskFilter(ServicePriceTableFilter):

    def get_delegation_queryset(self):
        qs = super().get_delegation_queryset()
        dynamic_query = Q()
        task = self.data.get('task')
        type_task = self.data.get('type_task')
        type_task_main = self.data.get('type_task_main', [])
        networks = self.data.get('networks')
        dynamic_query.add(
            Q(
                # seleciona os precos que tenham tipo de servico igual o tipo de servico da OS e que sejam
                # do mesmo escritorio da OS
                Q(
                    Q(type_task=type_task) | Q(type_task=None)
                ),
                Q(office=task.office)
            ) |
            Q(
                # selecina os precos que estejam no mesmo tipo de servico principal do tipo de servico da OS
                # e que sejam do mesmo escritorio da OS
                Q(type_task__type_task_main__in=type_task_main),
                Q(office=task.office)
            ) |
            Q(
                # seleciona os precos que estejam no mesmo tipo de servico principal do tipo de servico da OS
                # e que sejam de categoria Publica
                Q(type_task__type_task_main__in=type_task_main),
                Q(policy_price__category=CategoryPrice.PUBLIC)) |
            Q(
                # seleciona os precos que estejam no mesmo tipo de servico principal do tipo de servico da OS
                # e que pertencam a mesma rede do escritorio da OS,
                # desde que nao sejam precos do escritorio da OS
                Q(type_task__type_task_main__in=type_task_main),
                Q(office_network__in=networks),
                ~Q(office=task.office)
            ), Q.AND
        )
        return qs.filter(dynamic_query)


class ServicePriceTableDefaultFilter(ServicePriceTableFilter):

    def get_delegation_queryset(self):
        qs = super().get_delegation_queryset()
        dynamic_query = Q()
        court_district = self.data.get('court_district')
        state = self.data.get('state')
        complement = self.data.get('complement')
        city = self.data.get('city')
        client = self.data.get('client')
        dynamic_query.add(Q(Q(court_district=court_district) | Q(court_district=None)), Q.AND)
        dynamic_query.add(Q(Q(state=state) | Q(state=None)), Q.AND)
        dynamic_query.add(Q(Q(court_district_complement=complement) | Q(court_district_complement=None)), Q.AND)
        dynamic_query.add(Q(Q(city=city) | Q(city=None)), Q.AND)
        dynamic_query.add(Q(Q(client=client) | Q(client=None)), Q.AND)
        return qs.filter(dynamic_query)
