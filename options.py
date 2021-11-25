import dbs;
import pdb;

def setup_options(c):
    # pdb.set_trace()
    clear_options()
    options = get_options(dbs.staging)
    write_options_table(options)
    update_options()    # Deprecate?
    
def clear_options():
    dbs.live.execute("delete from wp_options")
    dbs.liveDb.commit()

def prepare_options(options):
    return options

def get_options(c):
    c.execute("select * from wp_options")
    return dbs.staging.fetchall()

def write_options_table(options):
    for option in options:
        option_name = option["option_name"]
        option_value = option["option_value"]
        option_value_corrected = correct_option_value_for_url(option_value)
        autoload = option["autoload"]
        sql = "INSERT into wp_options (option_name, option_value, autoload) values (%s, %s, %s)"
        dbs.live.execute(sql, (option_name, option_value, autoload))
    dbs.liveDb.commit()



def correct_option_value_for_url(option_value):
    staging_url = "http://visibleimage.staging.wpengine.com"
    if staging_url in option_value:
        corrected_url = option_value.replace(staging_url, "https://vitestmigrate.wpengine.com")
        print(f"Corrected URL in options: {corrected_url}")
        return corrected_url
    else:
        return option_value

def update_options():

    updates= {
        'home': dbs.siteurl,
        'siteurl': dbs.siteurl
    }

    for field_name in updates.keys():
        update_option(field_name, updates[field_name])


def update_option(key, value):
    sql = "update wp_options set option_value = %s where option_name = %s"
    dbs.live.execute(sql, (value, key))
