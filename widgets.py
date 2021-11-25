import dbs

def get_hero_attachment_metas():
    query = "select * from wp_postmeta where meta_key like 'hero%hero_image';"
    dbs.staging.execute(query)
    metas = dbs.staging.fetchall()
    return metas

# At end of script, we manually set some things.
def update():
   # Not implemented, but potentially we could manually set the correct WP term ids for stamps, stencils, dies
   pass

