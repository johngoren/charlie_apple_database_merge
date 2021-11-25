import pdb

def get_all_post_meta(c):
    queryAllPostMeta = "SELECT * FROM wp_postmeta"
    c.execute(queryAllPostMeta)
    metas = c.fetchall()
    return metas

def get_post_meta_for_posts(c, post_id_list):
    text_list = [str(p) for p in post_id_list]
    sql_values = ",".join(text_list)
    sql = f'SELECT meta_id, post_id, meta_key, meta_value FROM wp_postmeta WHERE post_id IN ({sql_values})'
    c.execute(sql)
    results = c.fetchall()
    return list(results)

def get_meta_for_type(category, c):
    query = f'SELECT meta_id, post_id, meta_key, meta_value FROM wp_posts p LEFT JOIN wp_postmeta x ON (p.ID = x.post_id) WHERE p.post_type="{category}"'
    c.execute(query)
    metas = c.fetchall()
    return metas

def get_posts_of_type(category, c):
    query = f'SELECT * FROM wp_posts WHERE post_type="{category}" AND post_status="publish"'
    c.execute(query)
    return c.fetchall()

def get_all_posts(c):
    query = f'SELECT * FROM wp_posts'
    c.execute(query)
    return c.fetchall()

def get_terms(c):
    query = f'SELECT * FROM wp_terms'
    c.execute(query)
    return c.fetchall()

def get_term_taxonomy(c):
    query = f'SELECT * FROM wp_term_taxonomy'
    c.execute(query)
    return c.fetchall()

def get_term_relationships(c):
    query = f'SELECT * FROM wp_term_relationships'
    c.execute(query)
    return c.fetchall()

def get_term_meta(c):
    query = f'SELECT * FROM wp_termmeta'
    c.execute(query)
    return c.fetchall()

def get_post_for_id(id, cursor):
    query = f'SELECT * FROM wp_posts WHERE id={id}'
    cursor.execute(query)
    result = cursor.fetchall()
    # print(result)

def get_meta_for_id(id, cursor):
    query = f'SELECT * FROM wp_postmeta WHERE post_id={id}'
    cursor.execute(query)
    result = cursor.fetchall()
    # print(result)