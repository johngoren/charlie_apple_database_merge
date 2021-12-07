# Visible Import SQL Migration Script

# Overview
This package is a Python command line script that reconciles two locally-run databases, Live and Production. It comes as a whole directory containing the main executable, Migrate.py, and its helper files, but let me know if you would prefer it be compiled into a single one-file executable.

# Setup

You will need:
* Python 3
* A MySQL server with the two source databases imported (under the names "live" and whatever name is assigned to the production DB in the *config.yaml* config file, e.g. "wp_visibleimage")
* Python dependencies for SQL (mysqlclient, mysql-connector-python, yaml) installed via pip (and any others that the script asks for)

To configure the script to connect with the two databases, you will need to enter credentials for a DB user possessing all access privileges into the config file, Config.yaml. Otherwise you will run into an ACCESS_DENIED error.

To make sure the script finds your Python correctly if it's somewhere other than /usr/bin/env, you may need to change the filepath at the top of Migrate.py.

To output a log file instead of printing to the screen, you can set Logging to True in the main file, which is Migrate.py.



# Use

1. Once the script can successfully connect to the two databases, and has command line execution rights, you should be able to run it as a shell command: **./migrate.py**
2. Depending on your machine, the process may run for upwards of 15 minutes. (Sorry, I didn't get around to optimising/consolidating the many queries into something more efficient with JOINs etc.)
3. When it's done, your Live DB will have been modified. I have been using mysqldump to export the updated Live into an .SQL file.
4. I then upload (via scp) and import that .SQL file into the Test Migration environment, using WP CLI import {dumpname}. This has been going smoothly on the Test Migrate site but hung last Friday when performed on Production.
5. Post-import cleanup (below)
6. Copying this environment over in WP Engine (while making appropriate URL changes to wp_options)

# Post-import cleanup

The following WordPress front-end issues will remain after import:

* You'll want to import ACF field groups using the export .JSON from Staging (provided here in /json/)
* Home's ACF widgets need to have their categories, posts and two Hero images set -- been doing this manually.
* Main and footer menus need to be set up after export (due to the script's conservative approach to taxonomies to avoid breaking product categories)
* Category Images need to have their GUIDs search-and-replaced (in wp_options) to point to the correct server.
* Other wp_options should be search-and-replaced to indicate new site URL.

The modified DB is also larger than it was before being processed. I'm not sure whether this causes RAM usage to climb a lot during "wp db import," but to reduce the risk of overwhelming the shared Production hosting on WPEngine (and to purge any duplicate metadata), you should slim it down through WP Optimise or a similar cleanup plugin before import.

# Other notes

* You can configure things like which keys and CPTs are affected, under Config.yaml.
* Former Post IDs of posts that have been remapped can be found under the wp_postmeta key "old_id".
* You'll see I just added "_price" to the list of protected keys in Config, as an example of how the script takes precautions to avoid overwriting live data.

Hope this works OK for you and let me know if you run into any problems. If you prefer I can probably book some time to just run the script on my desktop next week and hand over the output SQL.
