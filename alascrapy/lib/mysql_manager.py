import MySQLdb

from alascrapy.lib.log import log_exception


class MysqlManager(object):

    def __init__(self, project_conf, logger):
        self.db_host = project_conf.get("DATABASE", 'host')
        self.db_username = project_conf.get("DATABASE", 'username')
        self.db_password = project_conf.get("DATABASE", 'password')
        self.logger = logger

    def connect(self):
        return MySQLdb.connect(user=self.db_username,
                               passwd=self.db_password,
                               host=self.db_host,
                               charset="utf8",
                               use_unicode=True)

    def execute_select(self, query, args=None, batch_size=500):
        return_data = []
        connection = self.connect()
        cur = connection.cursor(MySQLdb.cursors.DictCursor)
        cur.arraysize = batch_size
        try:
            cur.execute(query, args)
        except Exception, e:
            log_exception(self.logger, e)
            raise e

        while 1:
            data = cur.fetchmany()
            if not data:
                break
            return_data = return_data + list(data)
        cur.close()
        connection.close()
        return return_data

    def start_transaction(self):
        connection = self.connect()
        try:
            return (connection, connection.cursor())
        except Exception, e:
            log_exception(self.logger,e)
            self.logger.info("Executed Rollback")
            connection.rollback()



    def execute_transaction(self, connection, cursor, query, args=None):
        try:
            cursor.execute(query, args)
        except Exception, e:
            log_exception(self.logger,e)
            if cursor is not None:
                self.logger.info("Executed Rollback, last query: " \
                        + cursor._last_executed)
                connection.rollback()

    def commit_transaction(self, connection, cursor):
        try:
            connection.commit()
        except Exception, e:
            log_exception(self.logger, e)
            if cursor is not None:
                self.logger.info("Executed Rollback")
                connection.rollback()
        finally:
            connection.close()
            if cursor is not None:
                cursor.close()
    
    def execute_to_fetch_list(self, query, args=None):
        connection = self.connect()
        cur = connection.cursor()
        try:
            cur.execute(query, args)
            data = cur.fetchall()
            data_list = [raw[0] for raw in data]
        except Exception, e:
            log_exception(self.logger, e)
            raise e

        cur.close()
        connection.close()
        return data_list

    def insert_gcse_results(self, query):
        connection = self.connect()
        cur = connection.cursor()
        cur.execute(query)
        connection.commit()

