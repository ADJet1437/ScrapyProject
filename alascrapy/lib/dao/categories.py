# -*- coding: utf-8 -*-
""" 
    The purpose of this module is to provide the necessary functions to
    manage the category data in the database .
"""
def load_current_categories(mysql_manager, source_id):
    categories = mysql_manager.execute_select(
        "SELECT OriginalCategoryName, do_not_load \
         FROM review.originalcategoryname2category_new\
         WHERE source_id=%s" % source_id)

    cat_dict = {}
    for category in categories:
        cat_dict[category["OriginalCategoryName"].lower()] = category
    return cat_dict


def insert_new_category(mysql_manager, category):
    insert_ocn_category = \
        """ INSERT INTO review.originalcategoryname2category_new(source_id,
                OriginalCategoryName, original_category_idstring,
                Category_new, category_id, do_not_load)
            VALUES(%s,%s,%s,'NEED TO DEFINE',-1, %s)"""
    ocn_params = (category["source_id"], category["category_path"],
                  category["category_string"], int(category['do_not_load']))

    connection, cursor = mysql_manager.start_transaction()
    mysql_manager.execute_transaction(connection, cursor, insert_ocn_category,
                                      args=ocn_params)
    mysql_manager.commit_transaction(connection, cursor)

def get_categories_to_load_from_source(mysql_manager, source_id, prefix):
    return mysql_manager.execute_select(
        """SELECT source_id, OriginalCategoryName, do_not_load, category_id 
           FROM review.originalcategoryname2category_new 
           WHERE source_id={source_id}
           AND do_not_load = 0 
           AND OriginalCategoryName RLIKE '^({prefix})[[:digit:]]+$'".format(source_id=source_id, prefix = prefix)
        """   
    )