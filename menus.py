import dbs

def purge():
    sql = "delete from wp_term_relationships where term_taxonomy_id=13 or term_taxonomy_id=15"
    dbs.live.execute(sql)
    dbs.liveDb.commit()
    print(f"Purged {dbs.live.rowcount} obsolete taxonomy relationships (menus)")