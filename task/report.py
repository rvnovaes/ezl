import xlsxwriter
import io


class BaseFormatCell(object):
    def __init__(self, workbook):
        self.cell_format = workbook.add_format()
        self.cell_format.set_border(1)
        self.cell_format.set_align('left')


class TitleFormatCell(BaseFormatCell):
    def __init__(self, workbook):
        super().__init__(workbook)
        self.cell_format.set_bold()
        self.cell_format.set_bg_color('silver')


class DateTimeFormatCell(BaseFormatCell):
    def __init__(self, workbook):
        super().__init__(workbook)
        self.cell_format.num_format = 'dd/mm/yy hh:mm'        


class MoneyFormatCell(BaseFormatCell):
    def __init__(self, workbook):
        super().__init__(workbook)
        self.cell_format.num_format = 'R$#.#0'


def format_boolean(value):
    if value:
        return 'SIM'
    return 'NÃO'


class DefaultXlsFile(object):
    def __init__(self, remove_timezone=True):
        self.output = io.BytesIO()
        self.workbook = xlsxwriter.Workbook(self.output, {'remove_timezone': remove_timezone})
        self.base_cell_format = BaseFormatCell(self.workbook)
        self.title_cell_format = TitleFormatCell(self.workbook)
        self.datetime_cell_format = DateTimeFormatCell(self.workbook)
        self.money_format = MoneyFormatCell(self.workbook)

    def get_worksheet(self):
        return self.workbook.add_worksheet()


class TaskToPayXlsx(DefaultXlsFile):
    def __init__(self, data, remove_timezone=True):
        super().__init__(remove_timezone)
        self.data = data
        self.columns = [
                    {'label': 'OS', 'size': 10},
                    {'label': 'Escritórioaaaa', 'size': 40},
                    {'label': 'Finalização', 'size': 15}, 
                    {'label': 'Serviço', 'size': 50}, 
                    {'label': 'Processo', 'size': 30}, 
                    {'label': 'Centro de custo', 'size': 30},
                    {'label': 'Comarca', 'size': 20},
                    {'label': 'UF', 'size': 5},
                    {'label': 'Cliente', 'size': 45},
                    {'label': 'Reembolsa valor', 'size': 20}, 
                    {'label': 'Parte adversa', 'size': 50}, 
                    {'label': 'OS original', 'size': 15},
                    {'label': 'Faturada', 'size': 10}, 
                    {'label': 'Transação via cartão', 'size': 10},
                    {'label': 'Valor Tabela', 'size': 10},
                    {'label': 'Comissão', 'size': 10},
                    {'label': 'Total', 'size': 10}
                ]

    def get_report(self): 
        worksheet = self.get_worksheet()
        worksheet.autofilter(0, 0, 50, 11)
        for col_num, column in enumerate(self.columns):        
            worksheet.set_column(col_num, col_num, column.get('size'))
            worksheet.write(0, col_num, column.get('label'), self.title_cell_format.cell_format)
        for row_num, item in enumerate(self.data, 1):
            worksheet.write(row_num, 0, item.get('parent_task_number'), self.base_cell_format.cell_format)
            worksheet.write(row_num, 1, item.get('office_name'), self.base_cell_format.cell_format)
            finished_date = item.get('finished_date').astimezone() \
                if item.get('finished_date') else ''
            if finished_date:
                worksheet.write_datetime(row_num, 2, finished_date, self.datetime_cell_format.cell_format)
            else:
                worksheet.write(row_num, 2, finished_date, self.datetime_cell_format.cell_format)
            worksheet.write(row_num, 3, item.get('type_task'), self.base_cell_format.cell_format)
            worksheet.write(row_num, 4, item.get('lawsuit_number'), self.base_cell_format.cell_format)
            worksheet.write(row_num, 5, item.get('cost_center'), self.base_cell_format.cell_format)
            worksheet.write(row_num, 6, item.get('court_district'), self.base_cell_format.cell_format)
            worksheet.write(row_num, 7, item.get('uf'), self.base_cell_format.cell_format)
            worksheet.write(row_num, 8, item.get('client_name'), self.base_cell_format.cell_format)
            worksheet.write(row_num, 9, format_boolean(item.get('client_refunds')), self.base_cell_format.cell_format)
            worksheet.write(row_num, 10, item.get('opposing_party'), self.base_cell_format.cell_format)
            worksheet.write(row_num, 11, item.get('task_legacy_code', item.get('parent_task_number')),
                            self.base_cell_format.cell_format)
            worksheet.write(row_num, 12, format_boolean(item.get('billing_date')), self.base_cell_format.cell_format)
            worksheet.write(row_num, 13, item.get('charge_id'), self.base_cell_format.cell_format)
            worksheet.write(row_num, 14, item.get('amount_delegated'), self.money_format.cell_format)
            worksheet.write(row_num, 15, item.get('fee'), self.money_format.cell_format)
            worksheet.write(row_num, 16, item.get('amount_to_pay'), self.money_format.cell_format)
        self.workbook.close()
        self.output.seek(0)
        return self.output


class ExportFilterTask(DefaultXlsFile):
    def __init__(self, data, remove_timezone=True):
        super().__init__(remove_timezone)
        self.data = data
        self.columns = [
                    {'label': 'Status', 'size': 10},
                    {'label': 'Nº da OS', 'size': 10},
                    {'label': 'Prazo', 'size': 15},
                    {'label': 'Serviço', 'size': 50},
                    {'label': 'Processo', 'size': 30},
                    {'label': 'Cliente', 'size': 45},
                    {'label': 'Parte Adversa', 'size': 45},
                    {'label': 'OS Original', 'size': 15},
                    {'label': 'Descrição', 'size': 50},
                    {'label': 'Solicitante', 'size': 45},
                    {'label': 'UF', 'size': 10},
                    {'label': 'Comarca', 'size': 20},
                    {'label': 'Vara', 'size': 20},
                    {'label': 'Correspondente', 'size': 45},
                    {'label': 'Data Solicitação', 'size': 15},
                ]

    def get_report(self):
        worksheet = self.get_worksheet()
        worksheet.autofilter(0, 0, self.data.__len__() + 1, 14)
        for col_num, column in enumerate(self.columns):
            worksheet.set_column(col_num, col_num, column.get('size'))
            worksheet.write(0, col_num, column.get('label'), self.title_cell_format.cell_format)
        for row_num, item in enumerate(self.data, 1):
            worksheet.write(row_num, 0, item.get('task_status'), self.base_cell_format.cell_format)
            worksheet.write(row_num, 1, item.get('task_number'), self.base_cell_format.cell_format)
            final_deadline_date = item.get('final_deadline_date').astimezone() \
                if item.get('final_deadline_date') else ''
            if final_deadline_date:
                worksheet.write_datetime(row_num, 2, final_deadline_date, self.datetime_cell_format.cell_format)
            else:
                worksheet.write(row_num, 2, final_deadline_date, self.datetime_cell_format.cell_format)
            worksheet.write(row_num, 3, item.get('type_task_name'), self.base_cell_format.cell_format)
            worksheet.write(row_num, 4, item.get('law_suit_number'),
                            self.base_cell_format.cell_format)
            worksheet.write(row_num, 5, item.get('client'),
                            self.base_cell_format.cell_format)
            worksheet.write(row_num, 6, item.get('opposing_party'),
                            self.base_cell_format.cell_format)
            worksheet.write(row_num, 7, item.get('origin_code'), self.base_cell_format.cell_format)
            worksheet.write(row_num, 8, item.get('description'),
                            self.base_cell_format.cell_format)
            worksheet.write(row_num, 9, item.get('asked_by_legal_name'),
                            self.base_cell_format.cell_format)
            worksheet.write(row_num, 10, item.get('state_initials'),
                            self.base_cell_format.cell_format)
            worksheet.write(row_num, 11, item.get('court_district_name'),
                            self.base_cell_format.cell_format)
            worksheet.write(row_num, 12, item.get('court_division_name'),
                            self.base_cell_format.cell_format)
            worksheet.write(row_num, 13, item.get('executed_by_legal_name'),
                            self.base_cell_format.cell_format)
            requested_date = item.get('requested_date').astimezone() \
                if item.get('requested_date') else ''
            if requested_date:
                worksheet.write_datetime(row_num, 14, requested_date, self.datetime_cell_format.cell_format)
            else:
                worksheet.write(row_num, 14, requested_date, self.datetime_cell_format.cell_format)
        self.workbook.close()
        self.output.seek(0)
        return self.output
