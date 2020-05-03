import scrapy.settings as settings
from scrapy.exporters import CsvItemExporter

class ItemCSVExporter(CsvItemExporter):

    def __init__(self, *args, **kwargs):
        kwargs['encoding'] = 'utf-8'
        kwargs['delimiter'] = '\t'
        super(ItemCSVExporter, self).__init__(*args, **kwargs)