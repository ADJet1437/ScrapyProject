import MySQLdb
from traceback import format_exc
from alascrapy.pipelines import AlascrapyPipeline

class ReviewTextPipeline(AlascrapyPipeline):

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
        if item._name == "review":
            self.insert_review(item)

        return item

    def insert_review(self, item):
        try:
            self.cursor.execute("""INSERT IGNORE INTO temp.all_text_reviews
                                 (ProductName,
                                 TestDateText,
                                 Author,
                                 TestTitle,
                                 Source_ID,
                                 TestUrl,
                                 alltext)
                                 VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                                (self.validate_field(item, 'ProductName'),
                                 self.validate_field(item, 'TestDateText'),
                                 self.validate_field(item, 'Author'),
                                 self.validate_field(item, 'TestTitle'),
                                 self.validate_field(item, 'source_id', encode=False),
                                 self.validate_field(item, 'TestUrl'),
                                 self.validate_field(item, 'alltext'))
                                )

            self.conn.commit()

        except MySQLdb.Error as e:
            self.cursor.rollback()
            print "Error %d: %s\n%s" % (e.args[0], e.args[1], format_exc())

    def close_spider(self, spider):
        self.conn.close()
