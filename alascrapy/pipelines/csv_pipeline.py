from datetime import datetime
from os.path import join, exists
from os import system, rename, listdir, remove
import contextlib
import json
import socket
from shutil import copyfile

import pika
from alascrapy.spiders.base_spiders.amazon import AmazonReviewsSpider
from alascrapy.exporters.csv_item_exporter import CSVItemExporter
from alascrapy.pipelines import AlascrapyPipeline
from alascrapy.lib.log import log_exception
from alascrapy.items import ProductIdItem, ProductItem, ReviewItem


class CsvSavePipeline(AlascrapyPipeline):
    """
    Csv saver.
    While scrapy script works, the csv file is stored in WORK_DIR.
    When the script is finished, move the csv files to FIN_DIR
    and send MQ to load.

    Then load program will copy and delete the csv file.
    """

    def open_spider(self, spider):
        spider._csv_exporters = dict()
        spider._csv_files = list()

    def new_exporter(self, source_id, spider):
        project_conf = spider.project_conf
        running_directory = project_conf.get("OUTPUT", 'running_directory')
        timestamp = datetime.now().strftime('-%Y%m%d_%H%M%S-')

        csv_header = {'product': ["source_id",
                                  "source_internal_id",
                                  "ProductName",
                                  "OriginalCategoryName",
                                  "PicURL",
                                  "ProductManufacturer",
                                  "TestUrl"],
                      'product_id': ["source_id",
                                     "source_internal_id",
                                     "ProductName",
                                     "ID_kind",
                                     "ID_value",
                                     "ID_value_orig"],
                      'review': ["source_id",
                                 "source_internal_id",
                                 "ProductName",
                                 "SourceTestRating",
                                 "SourceTestScale",
                                 "TestDateText",
                                 "TestPros",
                                 "TestCons",
                                 "TestSummary",
                                 "TestVerdict",
                                 "Author",
                                 "DBaseCategoryName",
                                 "TestTitle",
                                 "TestUrl",
                                 "award",
                                 "AwardPic",
                                 "countries"]
                      }

        exportd = dict()
        for item_name, header in csv_header.items():
            if item_name == 'category':
                continue

            # Fun with plurals!
            if item_name == "product_id":
                filename = item_name + timestamp + str(source_id) + '.csv'
            else:
                filename = item_name + "s" + \
                    timestamp + str(source_id) + '.csv'

            # Open our shiny new CSV file and point the CsvItemExporter to it
            csv_file = open(join(running_directory, filename), 'w+b',
                            buffering=1)
            exporter = CSVItemExporter(csv_file, fields_to_export=header)
            exporter.start_exporting()

            # Add exporter to list of exporters for this source_id
            spider._csv_files.append((filename, csv_file))
            exportd[item_name] = exporter

        # Store all exporters for the present source_id
        spider._csv_exporters[source_id] = exportd

    def _process_item(self, item, spider):
        spider_conf = spider.spider_conf

        if isinstance(item, ProductItem) or isinstance(item, ProductIdItem) \
            or isinstance(item, ReviewItem):
            # In case of siid is too long for raw schema,
            # we will truncate from the original siid by taking
            # 25 characters from the right side.
            siid = item.get('source_internal_id', None)
            if siid:
              if len(str(siid)) > 25:
                  _siid = siid[-25:]
                  item['source_internal_id'] = _siid

        if item._name != "category":
            source_id = item['source_id']
            if not source_id:
                source_id = spider_conf['source_id']

            if source_id not in spider._csv_exporters:
                self.new_exporter(source_id, spider)

            exporter = spider._csv_exporters[source_id][item._name]
            exporter.export_item(item)

        return item

    def push_mq(self, fileset, spider):
        project_conf = spider.project_conf
        username = project_conf.get("LOAD", "username")
        password = project_conf.get("LOAD", "password")
        load_host = project_conf.get("LOAD", "host")
        load_virtual_host = project_conf.get("LOAD", "virtual_host")
        queue_name = project_conf.get("LOAD", "queue")
        exchange = project_conf.get("LOAD", "exchange")
        routing_key = project_conf.get("LOAD", "routing_key")

        # TODO: why is this try catch everything?
        try:
            credsecurity = pika.PlainCredentials(username, password)
            parameters = pika.ConnectionParameters(
                host=load_host,
                virtual_host=load_virtual_host,
                credentials=credsecurity)
            connection = pika.BlockingConnection(parameters)
            with contextlib.closing(connection.channel()) as channel:
                channel.queue_declare(queue=queue_name, durable=True)
                send_mq_from_dev = project_conf.getboolean(
                    "OUTPUT", 'send_mq_request_local')
                servername = socket.gethostname()
                if send_mq_from_dev:
                    servername = 'alascrapy901'
                message = json.dumps(
                    {"host": servername,
                     "files": fileset}, sort_keys=True, indent=4)
                channel.basic_publish(exchange=exchange,
                                      routing_key=routing_key,
                                      body=message)
            connection.close()

        except Exception, e:
            spider._logger.info('Push MQ failed')
            log_exception(spider._logger, e)

    def close_spider(self, spider):
        project_conf = spider.project_conf
        running_directory = project_conf.get("OUTPUT", 'running_directory')
        finished_directory = project_conf.get("OUTPUT", 'finished_directory')
        log_dir = spider.get_spider_log_dir()

        send_mq = project_conf.getboolean("OUTPUT", 'send_mq_request')
        send_mq_from_dev = project_conf.getboolean("OUTPUT",
                                                   'send_mq_request_local')

        for item in spider._csv_exporters.itervalues():
            for exporter in item.itervalues():
                exporter.finish_exporting()

        for (filename, csvfile) in spider._csv_files:
            csvfile.close()
            system("chmod go+w %s" % join(running_directory, filename))
            rename(join(running_directory, filename),
                   join(finished_directory, filename))
            copyfile(join(finished_directory, filename),
                     join(log_dir, filename))

        # for AmazonReviewsSpiders, send_mq argument decides if a message should be sent to MQ
        if send_mq and (not isinstance(spider, AmazonReviewsSpider) or spider.send_mq):
            self.push_mq([join(finished_directory, filename)
                          for filename, _ in spider._csv_files], spider)
        if send_mq_from_dev:
            host_to = project_conf.get('LOAD', 'host_to_store_csv')
            for each_file in listdir(log_dir):
                if each_file.endswith('.csv'):
                    print(each_file)
                    scp = "scp {} alascrapy@{}:/var/local/load/finished".format(
                        join(log_dir, each_file), host_to)
                    system(scp)
            self.push_mq([join(finished_directory, filename)
                          for filename, _ in spider._csv_files], spider)
            print('Published msg to queue for loading re-scraped results')
