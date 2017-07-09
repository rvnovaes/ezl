# esse import deve vir antes de todos porque ele executa o __init__.py
from etl.advwin.advwin_ezl.advwin_ezl import GenericETL

from core.utils import LegacySystem
from core.models import Person
from lawsuit.models import Folder


class FolderETL(GenericETL):
    advwin_table = 'Jurid_Pastas'
    model = Folder
    query = "SELECT \n" \
            "    t1.Codigo_Comp, \n" \
            "    t1.Cliente \n" \
            "FROM " + advwin_table + " AS t1 \n" \
            "WHERE \n" \
            "    t1.Status = 'Ativa' AND \n" \
            "    t1.Codigo_Comp IS NOT NULL AND t1.Codigo_Comp <> '' AND \n" \
            "    t1.Cliente IS NOT NULL AND t1.Cliente <> '' AND \n" \
            "    t1.Codigo_Comp = ( \n" \
            "SELECT \n" \
            "    min(t2.Codigo_Comp) \n" \
            "FROM " + advwin_table + " AS t2 \n" \
            "WHERE \n" \
            "    t2.Status = 'Ativa' AND \n" \
            "    t2.Codigo_Comp IS NOT NULL AND t2.Codigo_Comp <> '' AND \n" \
            "    t2.Cliente IS NOT NULL AND t2.Cliente <> '' AND \n" \
            "    t1.Codigo_Comp = t2.Codigo_Comp)"
    has_status = True

    def load_etl(self, rows, user):
        log_file = open('log_file.txt', 'w')
        for row in rows:
            print(row)

            legacy_code = row['Codigo_Comp']
            customer_code = row['Cliente']

            instance = self.model.objects.filter(legacy_code=legacy_code,
                                                 system_prefix=LegacySystem.ADVWIN.value).first()

            person_customer = Person.objects.filter(legacy_code=customer_code,
                                                    system_prefix=LegacySystem.ADVWIN.value).first()
            if person_customer:
                if instance:
                    # use update_fields to specify which fields to save
                    # https://docs.djangoproject.com/en/1.11/ref/models/instances/#specifying-which-fields-to-save
                    instance.person_customer = person_customer
                    instance.is_active = True
                    instance.alter_user = user
                    instance.save(
                        update_fields=['person_customer',
                                       'is_active',
                                       'alter_date',
                                       'alter_user'])
                else:
                    obj = self.model(person_customer=person_customer,
                                     is_active=True,
                                     legacy_code=legacy_code,
                                     system_prefix=LegacySystem.ADVWIN.value,
                                     create_user=user,
                                     alter_user=user)
                    obj.save()

                super(FolderETL, self).load_etl(rows, user)
            else:
                log_file.write(str(row) + '\n')


if __name__ == "__main__":
    FolderETL().import_data()
