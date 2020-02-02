from scrapy.exporters import BaseItemExporter


class CSVItemExporter(BaseItemExporter):

    def __init__(self, csv_file, fields_to_export=None):
        self._headers_not_written = True
        self.csv_file = csv_file
        self.fields_to_export = fields_to_export

    def export_item(self, item):
        if self._headers_not_written:
            self._headers_not_written = False
            self._write_headers_and_set_fields_to_export(item)

        fields = self._get_serialized_fields(item)
        values = [x[1] for x in fields]
        self.writerow(values)

    def _write_headers_and_set_fields_to_export(self, item):
        if not self.fields_to_export:
            self.fields_to_export = item.fields.keys()
        self.writerow(self.fields_to_export)

    def _get_serialized_fields(self, item):
        """Return the fields to export as an iterable of tuples (name,
        serialized_value)
        """

        if self.fields_to_export is None:
            field_iter = item.fields.iterkeys()
        else:
            field_iter = self.fields_to_export

        for field_name in field_iter:
            if field_name in item:
                field = item.fields[field_name]
                value = self.delimit_string(item[field_name])
            else:
                value = None

            yield field_name, value

    def delimit_string(self, value):
        if isinstance(value, basestring):
            value = value.replace('\\', '\\\\') #escaping backslashes
            value = value.replace('"', '\\"')
            return value
        else:
            return value

    def writerow(self, fields):
        not_first = False

        for field in fields:
            if not isinstance(field, basestring):
                field = str(field)
            elif isinstance(field, unicode):
                field = field.encode('utf8')

            out_string = ""

            if not_first:
                out_string += ","

            if field!="None":
                out_string += '"'+field+'"'
            else:
                out_string += '""'

            self.csv_file.write(out_string)

            if not not_first:
                not_first = True

        self.csv_file.write("\n")
