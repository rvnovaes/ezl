from core.utils import LegacySystem
from etl.advwin.advwin_ezl.advwin_ezl import GenericETL
from task.models import TypeTask


class TypeTaskETL(GenericETL):
    model = TypeTask
    query = "SELECT  tm.Codigo,  tm.Descricao FROM Jurid_CodMov AS tm  " \
            "WHERE right(tm.Codigo, 1) <> '.'  " \
            "   AND (tm.UsarOS = 1 AND tm.UsarOS IS NOT NULL)  " \
            "   AND tm.Status = 'Ativo'  " \
            "   AND tm.Codigo= (SELECT MIN(tm2.codigo)    " \
            "                   FROM Jurid_CodMov AS tm2 WHERE tm.Descricao = tm2.Descricao)"
    advwin_table = 'Jurid_CodMov'
    has_status = True

    def load_etl(self, rows, user):
        for row in rows:
            code = row['Codigo']
            name = row['Descricao']

            # tem que verificar se é novo antes para não salvar o create_user ao fazer update
            instance = self.model.objects.filter(legacy_code=code,
                                                 system_prefix=LegacySystem.ADVWIN.value).first()
            if instance:
                instance.name = name
                instance.alter_user = user
                instance.is_active = True
                instance.save(update_fields=['is_active', 'name', 'alter_user', 'alter_date'])
            else:
                self.model.objects.create(name=name,
                                          is_active=True,
                                          legacy_code=code,
                                          system_prefix=LegacySystem.ADVWIN.value,
                                          create_user=user,
                                          alter_user=user)
        super(TypeTaskETL, self).load_etl(rows, user)


if __name__ == "__main__":
    TypeTaskETL().import_data()
