# -*- coding: utf-8 -*-
"""The purpose of this module is to provide the necessary functions to
   allow any spider to stop scraping once reached a certain point.

   The cases considered until the moment are:
    1- Found expert review equal or older that the newest
       expert review in our database for that particular source.
       (For this to be correct the website
        must have expert reviews sorted by date)
    2- Found an user review equal or older that the newest user review
       in our database for a particular product and source.
       (For this to be correct the product page
        in the website must have user reviews sorted by date)
    3- Found source_internal_id already existing in the DB.
       (For this approach to be correct the website
        must have products sorted by newest first.
        Probably hard to find websites where to use it)
    4- Found review_id already existing in the DB.
       (For this approach to be correct the website
        must have reviews sorted by newest first.
       Probably redundant with number 2 unless we are missing review date.)
"""
from datetime import datetime
from distutils.util import strtobool


def get_latest_pro_review_date(mysql_manager, source_id, category=None):
    if category:
        query = """SELECT r.TestDate
                   FROM review.reviews r
                   JOIN review.products p ON p.id=r.prdid
                   WHERE r.source_id=%s AND
                         r.DBaseCategoryName IN ('PRO', 'VPRO') AND
                         p.OriginalCategoryName=%s
                   ORDER BY r.TestDate DESC
                   LIMIT 1"""
        last_review = mysql_manager.execute_select(query, (source_id,
                                                           category['category_path']))
    else:
        query = """SELECT TestDate
                   FROM review.reviews
                   WHERE source_id=%s AND DBaseCategoryName IN ('PRO', 'VPRO')
                   ORDER BY TestDate DESC
                   LIMIT 1"""
        last_review = mysql_manager.execute_select(query, [source_id])

    if last_review:
        return last_review[0]['TestDate']
    return datetime.min


def get_incremental(mysql_manager, source_id, kind_name, kind_value):
    incremental_kind = mysql_manager.execute_select(
        """SELECT inc.id_value
           FROM review.product_id pi
           JOIN review.products p ON p.id=pi.prdid
           JOIN review.kinds k ON k.Kind = pi.Kind and k.Name =%s
           JOIN review.product_id inc ON pi.prdid=inc.prdid AND pi.kind=1056
           WHERE p.source_id=%s AND pi.ID_value_orig = %s
           LIMIT 1""", (kind_name, str(source_id), kind_value))

    if incremental_kind:
        return strtobool(incremental_kind[0]['id_value'])
    return None


def update_incremental(mysql_manager, source_id, kind_name, kind_value,
                       incremental):
    update_incremental_query = """UPDATE review.product_id pi
           JOIN review.products p ON p.id=pi.prdid
           JOIN review.kinds k ON k.Kind = pi.Kind and k.Name =%s
           JOIN review.product_id inc ON pi.prdid=inc.prdid AND pi.kind=1056
           SET inc.id_value='%s' AND pi.ID_value_orig='%s'
           WHERE p.source_id=%s AND pi.ID_value_orig = %s"""

    params = (kind_name, incremental, incremental, str(source_id), kind_value)

    connection, cursor = mysql_manager.start_transaction()
    mysql_manager.execute_transaction(connection, cursor,
                                      update_incremental_query,
                                      args=params)
    mysql_manager.commit_transaction(connection, cursor)


def get_latest_user_review_date(mysql_manager, source_id,
                                kind_name, kind_value):
    last_review = mysql_manager.execute_select(
        "SELECT r.TestDateText, r.TestDate\
         FROM review.reviews r\
         JOIN review.product_id pi ON r.PrdId = pi.PrdId\
         JOIN review.kinds k ON k.Kind = pi.Kind and k.Name =%s\
         WHERE source_id=%s AND DBaseCategoryName='USER' AND pi.ID_value_orig = %s\
         ORDER BY TestDate DESC\
         LIMIT 1",
        (kind_name, str(source_id), kind_value))

    if last_review and last_review[0]['TestDate']:
        return last_review[0]['TestDate']
    return datetime.min


def get_latest_user_review_date_by_sii(mysql_manager, source_id,
                                       source_internal_id):
    last_review = mysql_manager.execute_select(
        """SELECT r.TestDateText, r.TestDate
           FROM review.products_lookup pl
           JOIN review.reviews r ON r.PrdId = pl.PrdId
           WHERE pl.source_id=%s AND pl.source_internal_id = %s
           AND r.DBaseCategoryName='USER'
           ORDER BY TestDate DESC
           LIMIT 1""", (str(source_id), source_internal_id))

    if last_review:
        return last_review[0]['TestDate']
    return datetime.min


def get_all_review_urls(mysql_manager, source_id, review_type=None):
    if not review_type:
        results = mysql_manager.execute_select(
            """SELECT TestUrl
               FROM review.reviews
               WHERE source_id = %s""", (str(source_id))
        )
    else:
        results = mysql_manager.execute_select(
            """SELECT TestUrl
               FROM review.reviews
               WHERE source_id = %s
               AND DBaseCategoryName = %s""", (str(source_id), review_type)
        )

    return set(result['TestUrl'].rstrip('/') for result in results)


def is_product_in_db(mysql_manager, source_id, kind_name, kind_value):
    product_count = mysql_manager.execute_select(
        """SELECT count(0) as count
           FROM review.products p
           JOIN review.product_id pi ON p.id = pi.PrdId
           JOIN review.kinds k ON k.Kind = pi.Kind and k.Name =%s
           WHERE source_id=%s AND pi.ID_value_orig = %s""",
        (kind_name, str(source_id), kind_value))

    if product_count:
        return (product_count[0]['count'] > 0)
    return None


def is_product_in_db_by_sii(mysql_manager, source_id, sii):
    product_count = mysql_manager.execute_select(
        """SELECT count(0) as count
           FROM review.products p
           JOIN review.products_lookup pl ON p.id = pl.prdid
           WHERE pl.source_id=%s AND pl.source_internal_id=%s""",
        (str(source_id), sii))
    return (product_count[0]['count'] > 0)


def is_review_in_db(mysql_manager, source_id, review_internal_id):
    """Not implemented, there is no table for storing
       review_internal_id in the DB yet"""
    pass


def get_latest_review_date(mysql_manager, source_id):
    """We have been using this function: get_latest_pro_review_date
    for a long time, but this function only fetch the latest 
    review date of PRO review. Obviously, we can simplify this function
    to fit it for getting both lastest PRO and USER review date
    """
    query = """select TestDate from review.reviews where Source_ID = %s
     order by TestDate desc limit 1;
    """
    last_review = mysql_manager.execute_select(query, [source_id])
    if last_review:
        return last_review[0]['TestDate']
    return datetime.min


def get_youtube_channel_id_and_search_str(mysql_manager):
    channel_ids = []
    url_formats = []
    search_strings = []
    default_categories = []

    query = "select * from review.youtube_channels;"
    rows = mysql_manager.execute_select(query)
    for row in rows:
        channel_id = row['youtube_channel_id']
        url_format = row['url_format']
        search_string = row['search_string']
        category = row['default_category']
        channel_ids.append(channel_id)
        url_formats.append(url_format)
        search_strings.append(search_string)
        default_categories.append(category)
    return channel_ids, url_formats, \
        search_strings, default_categories
