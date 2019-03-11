import io
import xlsxwriter
from django.http import HttpResponse


class XLSXWriter():

    def __init__(self, filename, columns):
        self._last_row = -1
        self.filename = filename
        self.columns = columns
        self._output = io.BytesIO()
        self._workbook = xlsxwriter.Workbook(self._output,  {'remove_timezone': True})
        self._writer = self._workbook.add_worksheet()
        self.write_row(columns)

    def write_row(self, values):
        current_row = self._last_row + 1
        self._last_row = current_row

        for y, value in enumerate(values):
            self._writer.write(current_row, y, value)

    def close(self):
        self._workbook.close()

    def get_value(self):
        return self._output.getvalue()

    def get_http_response(self):
        xlsx_data = self.get_value()
        response = HttpResponse(
            xlsx_data,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = \
            'attachment; filename="{}"'.format(self.filename)
        return response
