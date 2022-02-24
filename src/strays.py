import mysql.connector

def init(arg):
    global strays_dict
    strays_dict = {}
    strays_dict = arg

# Reunite metadata with moved parents.

def reunite(c, db):
    reunite_count = 0
    stray_post_ids = strays_dict.keys()
    for old_post_id in stray_post_ids:
        new_post_id = strays_dict[old_post_id]
        sql = f"UPDATE wp_postmeta SET post_id={new_post_id} WHERE post_id={old_post_id}"
        print("Reuniting stray metadata")
        print(sql)
        reunite_count = reunite_count +1
        c.execute(sql)
    print(f"Reunited {reunite_count} strays")
    db.commit()