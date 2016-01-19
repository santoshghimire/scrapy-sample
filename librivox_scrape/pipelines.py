# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
import csv
from xlsxwriter.workbook import Workbook
from scrapy.exceptions import DropItem
from scrapy.pipelines.files import FilesPipeline
from librivox_scrape import settings
import scrapy
import requests
import subprocess
import sys
from scrapy import signals
from scrapy.exporters import CsvItemExporter


class CsvExportPipeline(object):

    fields_to_export = [
        'Title',
        'Author',
        'AuthorLifetime',
        'TotalLength',
        'Language',
        'Genre',
        'Readers',
        'NumberOfReaders',
        'WikipediaLink',
        'AuthorWikipediaLink',
        'CatalogedOnDate',
        'DescriptionText',
        'LibrivoxUrlOfTitle',
        'LinksToAll128kMp3Files',
        'HasCoverArt',
        'HasCdInsertArt'
    ]

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        FILES_STORE = settings.FILES_STORE
        self.file = open(FILES_STORE + 'Librivox-Book-List.csv', 'w+b')
        self.exporter = CsvItemExporter(self.file)
        self.exporter.fields_to_export = self.fields_to_export
        self.exporter.start_exporting()

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        FILES_STORE = settings.FILES_STORE
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        title_dir = item['Title']
        for each_char in invalid_chars:
            title_dir = title_dir.replace(each_char, '-')

        if not os.path.exists(FILES_STORE + title_dir):
            os.makedirs(FILES_STORE + title_dir)
        # write txt files
        for each_file in self.fields_to_export:
            txt_file = FILES_STORE + title_dir + '/' + each_file + '.txt'
            with open(txt_file, 'w') as outfile:
                outfile.write(item[each_file])
        return item

    def convert_csv_to_excel(self, csv_file, excel_file):
        workbook = Workbook(excel_file)
        worksheet = workbook.add_worksheet()
        with open(csv_file, 'rb') as f:
            reader = csv.reader(f)
            for r, row in enumerate(reader):
                for c, col in enumerate(row):
                    worksheet.write(r, c, col)
        workbook.close()


class LibrivoxFileDownloadPipeline(FilesPipeline):

    def get_media_requests(self, item, info):
        if item.get('file_urls'):
            for file_spec in item['file_urls']:
                yield scrapy.Request(
                    url=file_spec["file_url"],
                    meta={
                        "file_spec": file_spec,
                        "title_dir": item['Title']
                    }
                )

    def file_path(self, request, response=None, info=None):
        FILES_STORE = settings.FILES_STORE
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        title_dir = request.meta["title_dir"]
        for each_char in invalid_chars:
            title_dir = title_dir.replace(each_char, '-')
        if not os.path.exists(FILES_STORE + title_dir):
            os.makedirs(FILES_STORE + title_dir)
        file_path = title_dir + '/' + request.meta["file_spec"]["file_name"]
        return file_path

    def item_completed(self, results, item, info):
        if not item.get('file_urls'):
            raise DropItem("Item droped")
        file_paths = [x['path'] for ok, x in results if ok]
        file_urls = [x['url'] for ok, x in results if ok]
        if not file_paths:
            raise DropItem("Item contains no files")
        FILES_STORE = settings.FILES_STORE
        for count, each_file in enumerate(file_paths):
            # check mp3 files if they are corrupt or not
            if each_file[-4:] == '.mp3':
                each_file_abs = os.getcwd() + '/' + FILES_STORE + each_file
                if self.check_corrupt(each_file_abs):
                    alternate_file_url = file_urls[count].replace('128kb', '64kb')
                    if alternate_file_url.find('64kb') == -1:
                        alternate_file_url = alternate_file_url[:-4] + '_64kb' + alternate_file_url[-4:]
                    filename = FILES_STORE + item['Title'] + '/' + alternate_file_url.split('/')[-1]
                    with open(filename, 'wb') as handle:
                        response = requests.get(alternate_file_url, stream=True)
                        if not response.ok:
                            print('Error in process_item', alternate_file_url)
                        for block in response.iter_content(1024):
                            handle.write(block)
        return item

    def check_corrupt(self, file_path):
        output = subprocess.check_output(["mp3val", file_path])
        error_line = 'It seems that file is truncated or there is garbage at the end of the file'
        if output.find(error_line) > -1:
            return True
        else:
            return False
