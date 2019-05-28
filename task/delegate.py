from decimal import Decimal
from django.utils import timezone
from financial.models import ServicePriceTable
from task.utils import get_task_attachment, get_delegate_amounts, delegate_child_task


class DelegateTask(object):
    def __init__(self, request, form):
        self.request = request
        self.form = form

    @property
    def service_price_table(self):
        service_price_table_id = self.request.POST.get('servicepricetable_id', None)
        service_price_table = ServicePriceTable.objects.filter(
            id=service_price_table_id
        ).select_related('policy_price').first()
        return service_price_table

    def _get_instance_amounts(self):
        service_price_table = self.service_price_table
        amount_to_pay, amount_to_receive = get_delegate_amounts(self.form.instance,
                                                                service_price_table)
        return amount_to_pay, amount_to_receive

    def _update_amount_delegated(self):
        default_amount = self.form.instance.amount or Decimal('0.00')
        self.form.instance.amount_delegated = self.form.cleaned_data.get('amount', default_amount)

    def _update_instance_price_fields(self):
        self.form.instance.price_category = self.service_price_table.policy_price.category
        self.form.instance.rate_type_receive = self.service_price_table.rate_type_receive
        self.form.instance.rate_type_pay = self.service_price_table.rate_type_pay

    def delegate(self):
        self.form.instance.delegation_date = timezone.now()
        if not self.form.instance.person_distributed_by:
            self.form.instance.person_distributed_by = self.request.user.person

        get_task_attachment(self, self.form)
        if self.service_price_table:
            self._update_instance_price_fields()
            self._update_amount_delegated()
            amount_to_pay, amount_to_receive = self._get_instance_amounts()

            self.form.instance.amount_to_pay = amount_to_pay
            delegate_child_task(self.form.instance,
                                self.service_price_table.office_correspondent,
                                self.service_price_table.type_task,
                                amount_to_receive)
            self.form.instance.person_executed_by = None

        return self.form
