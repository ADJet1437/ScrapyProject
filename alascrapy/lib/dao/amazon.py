import datetime

def get_feed_categories(mysql_manager, source_id):
    feeds = mysql_manager.execute_select(
        """ SELECT feed_name, last_feed_date
            FROM feed_in_conf.alascrapy_amazon_feeds
            WHERE source_id=%s""" % source_id)
    return feeds

def update_feed_category(mysql_manager, feed_name, source_id, last_date):
    update_feed_query = \
        """ UPDATE feed_in_conf.alascrapy_amazon_feeds
            SET last_feed_date=%s
            WHERE source_id=%s AND feed_name=%s"""
    params = (last_date, source_id, feed_name)

    connection, cursor = mysql_manager.start_transaction()
    mysql_manager.execute_transaction(connection, cursor, update_feed_query,
                                      args=params)
    mysql_manager.commit_transaction(connection, cursor)

