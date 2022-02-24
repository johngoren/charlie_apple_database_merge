import dbs;
import conversion

def update():
    outdated_thumbs = get_all_thumb_metas()
    for thumb_meta in outdated_thumbs:
        obsolete_thumbnail_id = thumb_meta["meta_value"]
        new_id = conversion.get_new_id(obsolete_thumbnail_id)
        if new_id is not None:
            update_thumbnail_meta(obsolete_thumbnail_id, new_id)
        dbs.liveDb.commit()


def get_all_thumb_metas():
    sql = "select * from wp_postmeta where meta_key='_thumbnail_id'"
    dbs.live.execute(sql)
    return dbs.live.fetchall()

def update_thumbnail_meta(old_id, new_id):
    print(f"Updating ID of thumbnail from {old_id} to {new_id}.")
    sql = f"UPDATE wp_postmeta SET meta_value = {new_id} WHERE meta_key='_thumbnail_id' AND meta_value = {old_id}"
    dbs.live.execute(sql)
