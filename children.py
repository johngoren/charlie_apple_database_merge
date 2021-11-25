import dbs
import conversion

def reunite(posts):
    reunion_count = 0
    for post in posts:
        parent = post["post_parent"]
        post_id = post["ID"]
        forwarding_id = conversion.get_new_id(parent)
        if forwarding_id is not None:
            print(f"Reuniting post {post_id} with new parent who has moved from {parent} to {forwarding_id}")
            reunion_count = reunion_count + 1
            sql = f"UPDATE wp_posts SET post_parent={forwarding_id} where id={post_id}"
            print(sql)
            dbs.live.execute(sql)
    print(f"Reunions with children: {reunion_count}")
    dbs.liveDb.commit()
