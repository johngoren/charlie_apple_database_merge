import mysql
from wordpress import replace_single_wordpress_post, insert_single_wordpress_post, insert_single_wordpress_meta
from dbs import preserve_these_keys_on_live

def insert_live_products(c, products):
    for product in products:
        insert_live_product(product)

def insert_live_products_meta(c, metas):
    safe_metas = strip_unwanted_keys_from_metas(metas)
    for meta in safe_metas:
        insert_live_product_meta(c, meta)

def insert_live_product(c, product):
    replace_single_wordpress_post(c, product)

def insert_live_product_meta(c, meta):
    insert_single_wordpress_meta(c, meta)

def strip_unwanted_keys_from_metas(metas):
    return [x for x in metas if x not in preserve_these_keys_on_live ]
    
def insert_all_other_staging_posts(c, posts):
    ids = [x["ID"] for x in posts]
    for post in posts:
        insert_single_wordpress_post(c, post)
        # TODO key redirect

def insert_all_other_staging_meta(c, metas):
    for meta in metas:
        insert_single_wordpress_meta(c, meta)

def insert_all_other_staging_tables(c, posts):
    print("TODO bring over any other tables from Staging.")
