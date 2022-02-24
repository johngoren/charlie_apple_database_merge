import dbs
import pdb

def init(arg):
    global conversion_dict, orders_list
    conversion_dict = {}
    orders_list = []
    conversion_dict = arg

def set_old_id(old_id, new_id):
    sql = f"insert into wp_postmeta (post_id, meta_key, meta_value) values ({new_id}, 'old_id', {old_id})"
    dbs.live.execute(sql)
    dbs.liveDb.commit()

def get_old_id(new_id):
    sql = f'select meta_value from wp_postmeta where post_id={new_id} and meta_key="old_id"'
    dbs.live.execute(sql)
    row = dbs.live.fetchone()
    if row is not None:
        return row['meta_value']
    else:
        return new_id

def get_new_id(old_id):
    sql = f'select post_id from wp_postmeta where meta_key="old_id" and meta_value={old_id}'
    dbs.live.execute(sql)
    row = dbs.live.fetchone()
    if row is not None:
        return row['post_id']

def record_forwarding_address(old_id, new_id):
    conversion_dict[old_id] = new_id
    set_old_id(old_id, new_id)
