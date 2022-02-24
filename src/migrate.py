#!/usr/bin/env python3


import mysql.connector
import pdb
from dbs import staging, live, liveDb, dont_bring_these_product_keys_over_from_staging, dont_bring_these_post_types_over_from_staging, siteurl
from queries import get_all_posts, get_post_meta_for_posts, get_terms, get_term_taxonomy, get_term_relationships, get_posts_of_type, get_meta_for_type, get_term_meta
from products import drop_obsolete_products_posts, insert_live_products, insert_fresh_live_products_meta, preserve_product_meta, restore_preserved_product_meta, build_strays_dict, new_product_ids
from insert import insert_all_other_staging_posts, insert_all_other_staging_meta
from wordpress import delete_obsolete_posts_and_pages, insert_single_wordpress_meta, replace_term_relationships
from colors import bcolors
import conversion
import strays
import options
import children
import tax
import thumbnails
import menus
import widgets
import sys

# Note that during the writing of this script, I realized the latter style of imports was more pythonic.


logging = False

POST_TYPE_PRODUCT = "product"
POST_TYPE_COUPON = "shop_coupon"
POST_TYPE_ORDER = "shop_order"  
POST_TYPE_REFUND = "shop_order_refund"  


def main():
    if logging==True:
        log = open("migrate.log", "a")
        sys.stdout = log

    print(f"{bcolors.HEADER}*** Charlie Apple import script ***\n")

    global posts_staging, posts_live, meta_staging, meta_live, products_staging, products_live, meta_products_staging_filtered
    existing_products_id_list = get_products_id_list()

    input(f'{bcolors.OKCYAN}Press Enter to continue...')


    # # 0. Clearing out obsolete data.
    print(f"{bcolors.LIVE}Purging obsolete posts and pages from Live.")
    delete_obsolete_posts_and_pages(live)   
    menus.purge()

    # 1. Get all non-draft Product posts and their associated metadata

    products_staging = get_products(staging)

    print(f"{bcolors.STAGING}Found {len(products_staging)} products to carry over from Staging.")
    products_staging_meta = get_meta_for_type("product", staging)
    products_staging_meta_with_stocking_and_pricing_filtered_out = [p for p in products_staging_meta if is_among_desired_product_meta(p)]

    free_of_unwanted_keys = test_we_dont_have_unwanted_keys(products_staging_meta_with_stocking_and_pricing_filtered_out)
    assert free_of_unwanted_keys == True

    conversion.init(build_lookup_table())
    print(conversion.conversion_dict)

    products_staging_meta_remapped = remap_metas_to_new_IDs(products_staging_meta_with_stocking_and_pricing_filtered_out)

    print(f'{bcolors.LIVE}{len(products_staging)} fresh products to insert into Live.')         
    # So these have to keep the same IDs -- if they already exist in the database -- but have new ones if they don't.

    print(f'{bcolors.LIVE}{len(products_staging_meta_remapped)} fresh product meta to insert into Live.')

    # 2. Write these new products to Live!
    preserved_product_meta = preserve_product_meta(live)    

    drop_obsolete_products_posts(live)

    print(f'{bcolors.LIVE}Inserting fresh product posts.')
    insert_live_products(live, products_staging, existing_products_id_list)   # At the same original IDs so that we don't disrupt ongoing WooCommerce foreign key relationships.

    print("Inserting fresh product metadata.")
    insert_fresh_live_products_meta(live, products_staging_meta_remapped)

    print("Inserting preserved product metadata.")
    restore_preserved_product_meta(live, preserved_product_meta)   

    strays.init(build_strays_dict(live))

 
    terms_staging = get_terms(staging)
    term_taxonomy_staging = get_term_taxonomy(staging)
    term_relationships_staging = get_term_relationships(staging)
    term_relationships_staging_remapped = remap_relationships_to_new_IDs(term_relationships_staging) 
    term_metas = get_term_meta(staging)

    all_other_staging_posts = get_all_other_staging_posts() #
    all_other_staging_meta = get_all_other_staging_post_meta(all_other_staging_posts) # Except...

    # 4. Post it while preserving protected tables, post types and metas.

    print(f"{bcolors.LIVE}Restoring {len(all_other_staging_posts)} other staging posts (remapped with new id)")
    insert_all_other_staging_posts(live, all_other_staging_posts)
    all_other_staging_meta_remapped = remap_metas_to_new_IDs(all_other_staging_meta)
    print(f"{bcolors.LIVE}Restoring {len(all_other_staging_meta_remapped)} other staging post meta (remapped with new post_id)")
    insert_all_other_staging_meta(live, all_other_staging_meta_remapped)

    print(f"{bcolors.LIVE}Restoring {len(term_relationships_staging_remapped)} taxonomy term relationships (remapped with new object_id)")
    replace_term_relationships(live, term_relationships_staging_remapped)

    print(f"Writing all other taxonomy data")
    tax.write_terms(terms_staging)
    tax.write_term_taxonomy(term_taxonomy_staging)
    tax.write_term_metas(term_metas)


    
    # The six new products need to be treated differently because they didn't exist before Staging
    stray_meta_count = 0
    strays_metas = get_post_meta_for_posts(staging, new_product_ids)
    for meta in strays_metas:
        stray_meta_count = stray_meta_count + 1
        old_id = meta["post_id"]
        insert_single_wordpress_meta(live, meta)
        print(f"Inserting stray meta for post {old_id}")
    print(f"{stray_meta_count} stray metas inserted")

    # Update those metas we just posted so that they find their new IDs.
    strays.reunite(live, liveDb)


    all_posts = get_all_posts(live)
    print("Reuniting children with parents that may have moved")
    children.reunite(all_posts)
    options.setup_options(live) 
    thumbnails.update()

    do_final_report()

    staging.close()
    live.close()

def build_lookup_table():
    meta_products_staging = get_meta_for_type("product", staging)
    all_meta_from_live = get_meta_for_type("product", live)
    skus_staging = [x for x in meta_products_staging if is_sku(x)]
    skus_live = [x for x in all_meta_from_live if is_sku(x)]
    return build_lookup_table_for_products(skus_staging, skus_live)

def get_all_other_staging_posts():
    all_posts = get_all_posts(staging)
    return [x for x in all_posts if is_among_desired_post_types(x)]

def get_all_other_staging_post_meta(posts):
    list_of_valid_post_ids = get_list_of_post_IDs(posts)
    all_meta_from_staging = get_post_meta_for_posts(staging, list_of_valid_post_ids)
    return all_meta_from_staging

def get_list_of_post_IDs(posts):
    return list(map(get_id, posts))

def get_id(post):
    return post["ID"]

def get_posts(c):
    return get_posts_of_type("post", c)

def get_products(c):
    return get_posts_of_type("product", c)

def get_pages(c):
    return get_posts_of_type("page", c)

def get_menus(c):
    return get_posts_of_type("menu", c)


# Begin products

def build_lookup_table_for_products(sku_entries_staging, sku_entries_live):
    print('Building lookup table for Products with mismatched post IDs')
    mismatches = 0

    lookupDictForLivePostIDs = {}

    for entry in sku_entries_staging:
        sku = entry['meta_value']
        stagingId = entry['post_id']          
        live_id_entries = [x for x in sku_entries_live if x['meta_value'] == sku]
        if live_id_entries:
            # Couldn't find anything.
            live_id = live_id_entries[0]['post_id']

            if stagingId == live_id:
                pass    # They match.
            else:
                lookupDictForLivePostIDs[stagingId] = live_id 
                mismatches = mismatches + 1

    return lookupDictForLivePostIDs

def get_equivalent_for_staging_post_id(id):
    sku = get_sku_for_id(id)
    return sku

def get_sku_for_id(id):
    skuQuery = f'SELECT * FROM wp_postmeta WHERE post_id={id} AND meta_key="_sku"'
    staging.execute(skuQuery)
    result = staging.fetchall()
    sku = result[0]['meta_value']
    return sku

def get_id_for_sku(sku):
    skuQuery = f'SELECT * FROM wp_postmeta WHERE meta_value="{sku}"'
    live.execute(skuQuery)
    result = live.fetchall()
    return result[0]['post_id']


# Begin remapping

def remap_posts_to_new_IDs(products):
    new_products = [remap_post(p) for p in products]
    return new_products

def remap_post(p):
    old_id = p["ID"]
    p["ID"] = remap_id(old_id)
    return p

def remap_meta(m):
    old_id = m["post_id"]
    new_id = remap_id(old_id)
    key = m["meta_key"]
    if new_id != old_id:
        print(f"Remapped metadata with key {key} from post {old_id} to {new_id}")
    m["post_id"] = new_id
    return m

def remap_meta_values(metas):
    return [remap_meta_value(m) for m in metas]

def remap_meta_value(m):
    old_id = m["meta_value"]
    new_id = remap_id(old_id)
    key = m["meta_key"]
    if new_id != old_id:
        print(f"Remapped metadata value with key {key} from post {old_id} to {new_id}")
    m["meta_value"] = new_id
    return m

def remap_id(old_id):
    if old_id in conversion.conversion_dict:
        return conversion.conversion_dict[old_id]
    return old_id

def remap_relationship(r):
    old_id = r["object_id"]
    r["object_id"] = remap_id(old_id)
    return r

def remap_metas_to_new_IDs(metas):
    print(f"Remapping {len(metas)} metadata Post IDs.")
    new_metas = [remap_meta(m) for m in metas]
    return new_metas

def remap_metas_to_new_values(metas):
    print(f"Remapping {len(metas)} metadata values")
    new_metas = [remap_meta_value(m) for m in metas]
    return new_metas

def remap_relationships_to_new_IDs(relationships):
    new_relationships = [remap_relationship(r) for r in relationships]
    return new_relationships

def replace_meta_values(metas):
    for meta in metas:
        replace_meta_value(meta)

def replace_meta_value(meta):
    id = (meta["meta_id"])
    new_value = (meta["meta_value"])
    sql = f"UPDATE wp_postmeta SET meta_value={new_value} WHERE meta_id={id}"
    print(sql)
    live.execute(sql)
    liveDb.commit()


# Begin filters

def filter_out_protected_keys(metas):
    return [m for m in metas if is_among_desired_product_meta(m["meta_key"])]

def is_sku(meta):
    if meta["meta_key"] == "_sku":
        if meta["meta_value"] == '':
            return False
        if meta["post_id"] == 275:
            return False # Blank.
        else:
            # print(meta["meta_value"])
            return True
    return False

def is_among_desired_product_meta(meta):
    if meta["meta_key"] in dont_bring_these_product_keys_over_from_staging:
        return False
    return True

def is_among_desired_post_types(post):
    if post["post_type"] in dont_bring_these_post_types_over_from_staging:
        return False
    if post["post_type"] == "product":
        return False # Because we already imported it.
    return True

def do_final_report():
    print(f"In the end our remapping table grew to {len(conversion.conversion_dict)} entries")

def get_products_id_list():
    query = "select id from wp_posts where post_type='product'"
    live.execute(query)
    result = live.fetchall()
    return [p['id'] for p in result]


def test_we_dont_have_unwanted_keys(metas):
    ok = True
    for meta in metas:
        if meta["meta_key"] in dont_bring_these_product_keys_over_from_staging:
            print(f"Unwanted key found: {meta['meta_key']}")
            ok = False
    return ok




if __name__ == "__main__":
    main()

