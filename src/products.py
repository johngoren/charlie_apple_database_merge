import mysql
from dbs import preserve_these_keys_on_live, liveDb
from wordpress import insert_single_wordpress_post, insert_single_wordpress_meta, replace_single_wordpress_post
import pdb
import conversion

new_product_ids = []
strays = {}

def drop_obsolete_products_posts(c):
    print("Deleting old products posts.")
    query = "DELETE FROM wp_posts WHERE post_type='product'"
    c.execute(query)
    liveDb.commit()
    print(c.rowcount, "records deleted")

def insert_live_products(c, products_staging_remapped, existing_products_id_list):
    insert_count = 0
    replace_count = 0

    for fresh_product in products_staging_remapped:
        post_id = fresh_product["ID"]
        if post_id not in existing_products_id_list:
            # print(f"{post_id} was not in existing products, so we are adding it.")
            insert_single_wordpress_post(c, fresh_product)
            insert_count = insert_count + 1
            new_product_ids.append(post_id)
        else:
            replace_single_wordpress_post(c, fresh_product)
            replace_count = replace_count + 1
    liveDb.commit()
    print(f"{insert_count} products inserted, {replace_count} products replaced")
    print("Found these new product IDs:")
    print(new_product_ids)

def insert_fresh_live_products_meta(c, products_staging_meta_remapped):
    ids = [x["meta_id"] for x in products_staging_meta_remapped]

    for fresh_meta in products_staging_meta_remapped:
        insert_single_wordpress_meta(c, fresh_meta)
    liveDb.commit()

def restore_preserved_product_meta(c, preserved_product_meta):
    print(f"Ready to insert {len(preserved_product_meta)} items of preserved product meta")
    for preserved_meta_item in preserved_product_meta:
        insert_single_wordpress_meta(c, preserved_meta_item)
    liveDb.commit()

def preserve_product_meta(c):
    try:
        sql_list = get_sql_list(preserve_these_keys_on_live)
        query = f'SELECT * FROM wp_postmeta WHERE meta_key IN ({sql_list})'
        c.execute(query)
        result = c.fetchall()
        if result is not None:
            print(f"Found {len(result)} items of Product metadata to preserve")
            return result
        else:
            print("Error: Couldn't find any Post Meta in our query!")
    except:
        print(f"Something went wrong while preserving metadata")

def get_sql_list(list):
    sql_list = ", ".join(f"'{key}'" for key in list)
    return f'{sql_list}'

def build_strays_dict(c):
    for new_product_id in new_product_ids:
        remap_stray_id(new_product_id)
    return strays

def remap_stray_id(product_id):
    fresh_id = conversion.conversion_dict[product_id]
    print(f"Remapping stray item {product_id} to {fresh_id}")
    strays[product_id] = fresh_id

