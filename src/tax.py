import dbs

# Everything but wp term relationships


###

def write_terms(terms):
    for term in terms:
        insert_new_term(term)
    dbs.liveDb.commit()

def insert_new_term(term):
    term_id = term["term_id"]
    name = term["name"]
    slug = term["slug"]
    term_group = term["term_group"]

    sql = "replace into wp_terms (term_id, name, slug, term_group) values (%s, %s, %s, %s)"
    dbs.live.execute(sql, (term_id, name, slug, term_group))



###


def write_term_taxonomy(term_taxonomies):
    for term_taxonomy in term_taxonomies:
        insert_new_term_taxonomy(term_taxonomy)
    dbs.liveDb.commit()

def insert_new_term_taxonomy(taxonomy_data):
    term_taxonomy_id = taxonomy_data["term_taxonomy_id"]
    term_id = taxonomy_data["term_id"]
    taxonomy = taxonomy_data["taxonomy"]
    description = taxonomy_data["description"]
    parent = taxonomy_data["parent"]
    count = taxonomy_data["count"]

    sql = "replace into wp_term_taxonomy (term_taxonomy_id, term_id, taxonomy, description, parent, count) values (%s, %s, %s, %s, %s, %s)"
    dbs.live.execute(sql, (term_taxonomy_id, term_id, taxonomy, description, parent, count))

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


###


def write_term_metas(term_metas):
    for term_meta in term_metas:
        insert_new_term_meta(term_meta)
    dbs.liveDb.commit()

def insert_new_term_meta(term_meta):
    meta_id = term_meta["meta_id"]
    term_id = term_meta["term_id"]
    meta_key = term_meta["meta_key"]
    meta_value = term_meta["meta_value"]

    sql = "replace into wp_termmeta (meta_id, term_id, meta_key, meta_value) values (%s, %s, %s, %s)"
    dbs.live.execute(sql, (meta_id, term_id, meta_key, meta_value))


