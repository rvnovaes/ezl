from django.db.models import Manager, QuerySet


class PersonManager(Manager):
    def get_queryset(self):
        return PersonManagerQuerySet(self.model, using=self._db)

    def active(self, *ar, **kw):
        return self.get_queryset().active(*ar, **kw)

    def correspondents(self, *ar, **kw):
        return self.get_queryset().correspondents(*ar, **kw)

    def requesters(self, *ar, **kw):
        return self.get_queryset().requesters(*ar, **kw)

    def finances(self, *ar, **kw):
        return self.get_queryset().finances(*ar, **kw)

    def services(self, *ar, **kw):
        return self.get_queryset().services(*ar, **kw)

    def active_offices(self, *ar, **kw):
        return self.get_queryset().active_offices(*ar, **kw)

    def inactive_offices(self, *ar, **kw):
        return self.get_queryset().inactive_offices(*ar, **kw)


class PersonManagerQuerySet(QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def correspondents(self, office_id=False):
        if office_id:
            return self.filter(
                auth_user__groups__name__startswith='{}-{}'.format(self.model.CORRESPONDENT_GROUP, str(office_id))
            ).order_by('name', 'auth_user').distinct('name', 'auth_user')

        return self.filter(auth_user__groups__name__startswith='{}-'.format(self.model.CORRESPONDENT_GROUP)).order_by(
                               'name', 'auth_user').distinct('name', 'auth_user')

    def requesters(self, office_id=False):
        if office_id:
            return self.filter(
                auth_user__groups__name__startswith='{}-{}'.format(self.model.REQUESTER_GROUP, str(office_id))
            ).order_by('name', 'auth_user').distinct('name', 'auth_user')

        return self.filter(
            auth_user__groups__name__startswith='{}-'.format(self.model.REQUESTER_GROUP)).order_by(
            'name', 'auth_user').distinct('name', 'auth_user')

    def finances(self, office_id=False):
        if office_id:
            return self.filter(
                auth_user__groups__name__startswith='{}-{}'.format(self.model.FINANCE_GROUP, str(office_id))
            ).order_by('name', 'auth_user').distinct('name', 'auth_user')

        return self.filter(
            auth_user__groups__name__startswith='{}-'.format(self.model.FINANCE_GROUP)).order_by(
            'name', 'auth_user').distinct('name', 'auth_user')

    def services(self, office_id=False):
        if office_id:
            return self.filter(
                auth_user__groups__name__startswith='{}-{}'.format(self.model.SERVICE_GROUP, str(office_id))
            ).order_by('name', 'auth_user').distinct('name', 'auth_user')

        return self.filter(
            auth_user__groups__name__startswith='{}-'.format(self.model.SERVICE_GROUP)).order_by(
            'name', 'auth_user').distinct('name', 'auth_user')

    def active_offices(self):
        return self.filter(
            officemembership__is_active=True).order_by('legal_name')

    def inactive_offices(self):
        return self.filter(
            officemembership__is_active=False).order_by('legal_name')
