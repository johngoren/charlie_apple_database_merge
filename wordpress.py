import mysql
import pdb
import datetime
from dbs import liveDb
import colors
import conversion

post_fields = ["ID", "post_author", "post_date", "post_date_gmt", "post_content", "post_title", "post_excerpt", "post_status", "comment_status", "ping_status", "post_password", "post_name", "to_ping", "pinged", "post_modified", "post_modified_gmt", "post_content_filtered", "post_parent", "guid", "menu_order", "post_type", "post_mime_type", "comment_count"]
meta_fields = ["meta_id", "post_id", "meta_key" , "meta_value"]
meta_parents_deleted_so_far = []

def replace_term_relationships(c, relationships):
    for relationship in relationships:
        replace_term_relationship(c, relationship)

def replace_term_relationship(c, relationship):
    object_id=relationship["object_id"] # TODO is this properly remapped?
    term_taxonomy_id=relationship["term_taxonomy_id"]
    term_order=relationship["term_order"]

    relationship_data = (object_id, term_taxonomy_id, term_order)
    
    query = "REPLACE INTO wp_term_relationships (object_id, term_taxonomy_id, term_order) VALUES (%s, %s, %s)"
    c.execute(query, relationship_data)
    liveDb.commit()

def delete_obsolete_posts_and_pages(c):
    ids = get_ids_for_old_posts_and_pages(c)
    delete_metas_for_post_ids(c, ids)
    query = "delete from wp_posts where post_type in ('page', 'post', 'project_gallery', 'wpcf7_contact_form', 'acf', 'acf-field', 'acf-field-group', 'attachment', 'nav_menu_item')"
    c.execute(query)
    print(f"{c.rowcount} rows deleted.")
    liveDb.commit()

def get_ids_for_old_posts_and_pages(c):
    query = "SELECT id from wp_posts WHERE post_type IN ('page', 'post', 'project_gallery', 'wpcf7_contact_form', 'acf', 'acf-field', 'acf-field-group', 'attachment', 'nav_menu_item')"
    c.execute(query)
    result = c.fetchall()
    dicts = list(result)
    return [x['id'] for x in dicts]

def delete_metas_for_post_ids(c, post_ids):
    for id in post_ids:
        delete_metas_for_post(c, id)

def delete_metas_for_post(c, post_id):
    query = f"DELETE FROM wp_postmeta WHERE post_id='{post_id}'"
    c.execute(query)
    liveDb.commit()

# TODO: Return the new autoincrement and put in conversion table and be sure to check conversion table later!!
def insert_single_wordpress_post(c, post):
    try:           
        old_id = post["ID"]

        data_post = get_post_data(post, has_id=False) 
        query = ("INSERT INTO wp_posts "
        "(post_author,post_date,post_date_gmt,post_content,post_title,post_excerpt,post_status,comment_status,ping_status,post_password,post_name,to_ping,pinged,post_modified,post_modified_gmt,post_content_filtered,post_parent,guid,menu_order,post_type,post_mime_type,comment_count) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "
        "%s, %s, %s, %s, %s)" )
        c.execute(query, data_post)
        new_id = c.lastrowid
        # pdb.set_trace()

        conversion.record_forwarding_address(old_id, new_id)
        liveDb.commit()
    except mysql.connector.errors.IntegrityError as err:
        print(err)

def replace_single_wordpress_post(c, post):
    try:           
        post_id = post["ID"]
        post_type = post["post_type"]
        # print(f'Inserting post {post_id}')

        data_post = get_post_data(post, has_id=True)
        # pdb.set_trace()
        query = ("REPLACE INTO wp_posts "
        "(ID,post_author,post_date,post_date_gmt,post_content,post_title,post_excerpt,post_status,comment_status,ping_status,post_password,post_name,to_ping,pinged,post_modified,post_modified_gmt,post_content_filtered,post_parent,guid,menu_order,post_type,post_mime_type,comment_count) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "
        "%s, %s, %s, %s, %s)" )
        c.execute(query, data_post)
    except mysql.connector.errors.IntegrityError:
        print(f"Integrity error while replacing: Post {post_id} of type {post_type} is probably a duplicate of an existing element")
    except:
        print(f"Something went wrong replacing Wordpress post {post_id} of type {post_type}")


def insert_single_wordpress_meta(c, meta):
    try:
        old_id = meta["meta_id"]
        # pdb.set_trace()
        # print(f'Inserting meta {old_id}')

        data_meta = get_meta_data(meta, has_id=False)

        query = ("INSERT INTO wp_postmeta "
        "(post_id,meta_key,meta_value) "
        "VALUES (%s, %s, %s)")
        c.execute(query, data_meta)
        new_id = c.lastrowid
        conversion.conversion_dict[old_id] = new_id
        liveDb.commit()
    except mysql.connector.errors.IntegrityError:
        print(f"Integrity error: Meta is probably a duplicate of an existing element")
        print(data_meta)
    except mysql.connector.errors.ProgrammingError:
        print(data_meta)

def delete_post(c, id):
    query = f"DELETE FROM wp_posts where ID={id}"
    c.execute(query)
    liveDb.commit()

def delete_meta_based_on_its_id(c, id):
    query = f"DELETE from wp_postmeta where meta_id={id}"
    print(".")
    c.execute(query)
    liveDb.commit()
 
def get_columns():
    return tuple(post_fields)

def get_post_data(post, has_id):
    result = []
    for field in post_fields:
        text = post[field]
        if isinstance(text, datetime.datetime):
            # pdb.set_trace()
            text = get_timestamp_for_date(text)
        if field=="post_date_gmt" and post["post_date_gmt"] is None:
            text = post["post_date"]
        if field=="post_modified_gmt" and post["post_modified_gmt"] is None:
            text = post["post_date"]
        result.append(text)
    if not has_id:
        result.pop(0)
    return tuple(result)

def get_meta_data(meta, has_id):
    result = []
    for field in meta_fields:
        text = meta[field]
        result.append(text)
    if not has_id:
        result.pop(0)
    return tuple(result)

def get_timestamp_for_date(date): 
    f = '%Y-%m-%d %H:%M:%S'
    return date.strftime(f)

