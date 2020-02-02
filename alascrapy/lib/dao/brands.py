# -*- coding: utf-8 -*-
""" 
    The purpose of this module is to provide the necessary functions to
    manage the brands data in the database .
"""
def load_icecat_brands_by_category_id(mysql_manager, category_id):
    brands = mysql_manager.execute_select(
        """SELECT b.Brand, b.BrandMasterName
           FROM review.al_ids a
           JOIN review.products p ON p.al_id=a.al_id AND p.source_id=10000001
           JOIN review.masterbrand b ON a.Brand=b.Brand
           WHERE a.category_id={category_id} AND a.Brand>0
           GROUP BY a.Brand;""".format(category_id=category_id))
    return brands