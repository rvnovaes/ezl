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

    def services(self, *ar, **kw):
        return self.get_queryset().services(*ar, **kw)

    def active_offices(self, *ar, **kw):
        return self.get_queryset().active_offices(*ar, **kw)

    def inactive_offices(self, *ar, **kw):
        return self.get_queryset().inactive_offices(*ar, **kw)


class PersonManagerQuerySet(QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def correspondents(self):
        return self.filter(auth_user__groups__name__startswith=self.model.CORRESPONDENT_GROUP + '-').order_by(
            'name', 'auth_user').distinct('name', 'auth_user')

    def requesters(self):
        return self.filter(auth_user__groups__name__startswith=self.model.REQUESTER_GROUP + '-').order_by(
            'name', 'auth_user').distinct('name', 'auth_user')

    def services(self):
        return self.filter(auth_user__groups__name__startswith=self.model.SERVICE_GROUP + '-').order_by(
            'name', 'auth_user').distinct('name', 'auth_user')

    def active_offices(self):
        return self.filter(officemembership__is_active=True)

    def inactive_offices(self):
        return self.filter(officemembership__is_active=False)
