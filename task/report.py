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


class TaskToPayXlsx(object):
    def __init__(self, data):
        self.data = data
        self.columns = [
                    {'label': 'OS', 'size': 10},
                    {'label': 'Escritório', 'size': 40}, 
                    {'label': 'Finalização', 'size': 15}, 
                    {'label': 'Serviço', 'size': 50}, 
                    {'label': 'Processo', 'size': 30}, 
                    {'label': 'Comarca', 'size': 20}, 
                    {'label': 'Cliente', 'size': 45}, 
                    {'label': 'Reembolsa valor', 'size': 20}, 
                    {'label': 'Parte adversa', 'size': 50}, 
                    {'label': 'Os original', 'size': 15}, 
                    {'label': 'Faturada', 'size': 10}, 
                    {'label': 'Valor', 'size': 10}, 
                ]

    def get_report(self): 
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output,  {'remove_timezone': True})
        base_cell_format = BaseFormatCell(workbook)
        title_cell_format = TitleFormatCell(workbook)
        datetime_cell_format = DateTimeFormatCell(workbook)
        money_format = MoneyFormatCell(workbook)
        worksheet = workbook.add_worksheet()
        worksheet.autofilter(0, 0, 50, 11)
        for col_num, column in enumerate(self.columns):        
            worksheet.set_column(col_num, col_num, column.get('size'))
            worksheet.write(0, col_num, column.get('label'), title_cell_format.cell_format)
        for row_num, item in enumerate(self.data, 1):
            worksheet.write(row_num, 0, item.get('parent_task_number'), base_cell_format.cell_format)      
            worksheet.write(row_num, 1, item.get('office_name'))        
            worksheet.write_datetime(row_num, 2, item.get('finished_date'), datetime_cell_format.cell_format)
            worksheet.write(row_num, 3, item.get('type_task'), base_cell_format.cell_format)
            worksheet.write(row_num, 4, item.get('lawsuit_number'), base_cell_format.cell_format)
            worksheet.write(row_num, 5, item.get('court_district'), base_cell_format.cell_format)
            worksheet.write(row_num, 6, item.get('client_name'), base_cell_format.cell_format)
            worksheet.write(row_num, 7, format_boolean(item.get('client_refunds')), base_cell_format.cell_format)
            worksheet.write(row_num, 8, item.get('opposing_party'), base_cell_format.cell_format)
            worksheet.write(row_num, 9, item.get('legacy_code', item.get('parent_task_number')), base_cell_format.cell_format)
            worksheet.write(row_num, 10, format_boolean(item.get('billing_date')), base_cell_format.cell_format)
            worksheet.write(row_num, 11, item.get('amount'), money_format.cell_format)
        workbook.close()
        output.seek(0)        
        return output


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
                    {'label': 'Comarca', 'size': 40},
                    {'label': 'UF', 'size': 10},
                    {'label': 'Data Solicitação', 'size': 15},
                ]

    def get_report(self):
        worksheet = self.get_worksheet()
        worksheet.autofilter(0, 0, 50, 11)
        for col_num, column in enumerate(self.columns):
            worksheet.set_column(col_num, col_num, column.get('size'))
            worksheet.write(0, col_num, column.get('label'), self.title_cell_format.cell_format)
        for row_num, item in enumerate(self.data, 1):
            worksheet.write(row_num, 0, item.get('task_status'), self.base_cell_format.cell_format)
            worksheet.write(row_num, 1, item.get('task_number'), self.base_cell_format.cell_format)
            worksheet.write_datetime(row_num, 2, item.get('final_deadline_date'), self.datetime_cell_format.cell_format)
            worksheet.write(row_num, 3, item.get('type_task__name'), self.base_cell_format.cell_format)
            worksheet.write(row_num, 4, item.get('movement__law_suit__law_suit_number'),
                            self.base_cell_format.cell_format)
            worksheet.write(row_num, 5, item.get('movement__law_suit__folder__person_customer__name'),
                            self.base_cell_format.cell_format)
            worksheet.write(row_num, 6, item.get('movement__law_suit__opposing_party'),
                            self.base_cell_format.cell_format)
            worksheet.write(row_num, 7, item.get('origin_code'), self.base_cell_format.cell_format)
            worksheet.write(row_num, 8, item.get('movement__law_suit__court_district__name'),
                            self.base_cell_format.cell_format)
            worksheet.write(row_num, 9, item.get('movement__law_suit__court_district__state__initials'),
                            self.base_cell_format.cell_format)
            worksheet.write_datetime(row_num, 10, item.get('requested_date'), self.datetime_cell_format.cell_format)
        self.workbook.close()
        self.output.seek(0)
        return self.output