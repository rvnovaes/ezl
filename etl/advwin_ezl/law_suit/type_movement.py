from core.utils import LegacySystem
from etl.advwin_ezl.advwin_ezl import GenericETL
from lawsuit.models import TypeMovement


class TypeMovementETL(GenericETL):
    import_query = "SELECT  tm.Codigo,  tm.Descricao FROM Jurid_CodMov AS tm  " \
                   "WHERE right(tm.Codigo, 1) <> '.'  " \
            "   AND (tm.UsarOS = 0 OR tm.UsarOS IS NULL)  " \
            "   AND tm.Status = 'Ativo'  " \
            "   AND tm.Codigo= (SELECT MIN(tm2.codigo)    " \
            "                   FROM Jurid_CodMov AS tm2 WHERE tm.Descricao = tm2.Descricao)"
    model = TypeMovement
    advwin_table = 'Jurid_CodMov'
    has_status = True

    def config_import(self, rows, user, rows_count):
        for row in rows:

            try:
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
                self.debug_logger.debug(
                    "Tipo Movimentacao,%s,%s,%s,%s,%s,%s,%s" % (str(name), str(True), str(code), str(LegacySystem.ADVWIN.value),
                                                     str(user.id),str(user.id),self.timestr))

            except Exception as e:
                self.error_logger.error(
                    "Ocorreu o seguinte erro na importacao de Tipo Movimentacao: " + str(rows_count) + "," + str(
                        e) + "," + self.timestr)


        super(TypeMovementETL, self).config_import(rows, user, rows_count)


if __name__ == '__main__':
    TypeMovementETL().import_data()
