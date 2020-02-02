import MySQLdb
from traceback import format_exc
from alascrapy.pipelines import AlascrapyPipeline

class MySQLDBPipeline(AlascrapyPipeline):

    def open_spider(self, spider):
        project_conf = spider.project_conf
        db_host = project_conf.get("DATABASE", 'host')
        db_username = project_conf.get("DATABASE", 'username')
        db_password = project_conf.get("DATABASE", 'password')

        self.conn = MySQLdb.connect(user=db_username,
                                    passwd=db_password,
                                    host=db_host,
                                    charset="utf8",
                                    use_unicode=True)
        self.cursor = self.conn.cursor()

    @staticmethod
    def validate_field(item, field, encode=True, encoding='utf-8'):
        if field in item:
            if item[field]:
                if encode:
                    return item[field].encode(encoding)
                else:
                    return item[field]
            else:
                return None
        else:
            return None

    def _process_item(self, item, spider):
        if item._name == "product":
            self.insert_product(item)
        elif item._name == "product_id":
            self.insert_product_id(item)
        elif item._name == "review":
            self.insert_review(item)

        return item

    def insert_product(self, item):
        try:
            self.cursor.execute("""INSERT IGNORE INTO ss_inbox_test.products
                                 (OriginalCategoryName,
                                 ProductName,
                                 source_internal_id,
                                 PicURL,
                                 ProductManufacturer,
                                 Source_id,
                                 TestUrl)
                                 VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                                (self.validate_field(item, 'OriginalCategoryName'),
                                 self.validate_field(item, 'ProductName'),
                                 self.validate_field(item, 'source_internal_id'),
                                 self.validate_field(item, 'PicURL'),
                                 self.validate_field(item, 'ProductManufacturer'),
                                 self.validate_field(item, 'source_id', encode=False),
                                 self.validate_field(item, 'TestUrl')))

            self.conn.commit()

        except MySQLdb.Error as e:
            self.cursor.rollback()
            print "Error %d: %s\n%s" % (e.args[0], e.args[1], format_exc())

    def insert_product_id(self, item):
        try:
            self.cursor.execute("""INSERT IGNORE INTO ss_inbox_test.product_id
                                 (ProductName,
                                 source_internal_id,
                                 ID_kind,
                                 ID_value,
                                 source_id)
                                 VALUES (%s, %s, %s, %s, %s)""",
                                (self.validate_field(item, 'ProductName'),
                                 self.validate_field(item, 'source_internal_id'),
                                 self.validate_field(item, 'ID_kind'),
                                 self.validate_field(item, 'ID_value'),
                                 self.validate_field(item, 'source_id', encode=False)))

            self.conn.commit()

        except MySQLdb.Error as e:
            self.cursor.rollback()
            print "Error %d: %s\n%s" % (e.args[0], e.args[1], format_exc())

    def insert_review(self, item):
        try:
            self.cursor.execute("""INSERT IGNORE INTO ss_inbox_test.reviews
                                 (ProductName,
                                 source_internal_id,
                                 SourceTestRating,
                                 SourceTestScale,
                                 TestDateText,
                                 TestPros,
                                 TestCons,
                                 TestSummary,
                                 TestVerdict,
                                 Author,
                                 DBaseCategoryName,
                                 TestTitle,
                                 Source_ID,
                                 TestUrl,
                                 Award,
                                 Award_pic,
                                 Award_countries)
                                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                (self.validate_field(item, 'ProductName'),
                                 self.validate_field(item, 'source_internal_id'),
                                 self.validate_field(item, 'SourceTestRating'),
                                 self.validate_field(item, 'SourceTestScale', encode=False),
                                 self.validate_field(item, 'TestDateText'),
                                 self.validate_field(item, 'TestPros'),
                                 self.validate_field(item, 'TestCons'),
                                 self.validate_field(item, 'TestSummary'),
                                 self.validate_field(item, 'TestVerdict'),
                                 self.validate_field(item, 'Author'),
                                 self.validate_field(item, 'DBaseCategoryName'),
                                 self.validate_field(item, 'TestTitle'),
                                 self.validate_field(item, 'source_id', encode=False),
                                 self.validate_field(item, 'TestUrl'),
                                 self.validate_field(item, 'award'),
                                 self.validate_field(item, 'AwardPic'),
                                 self.validate_field(item, 'countries')))

            self.conn.commit()

        except MySQLdb.Error as e:
            self.cursor.rollback()
            print "Error %d: %s\n%s" % (e.args[0], e.args[1], format_exc())

    def close_spider(self, spider):
        self.conn.close()
