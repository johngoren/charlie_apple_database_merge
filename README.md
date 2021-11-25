# Visible Import SQL Migration Script

# Overview
This package is a Python command line script that reconciles two locally-run databases, Live and Production.

# Setup

You will need:
* Python 3
* A MySQL or MariaDB server with the two source databases imported.

To configure the script to connect with the two databases, you will need to enter credentials for a DB user possessing all access privileges into the config file, Config.yaml. Otherwise you will run into an ACCESS_DENIED error.

To output a log file instead of printing to the screen, you can set Logging to True in the main file, which is Migrate.py.


# Use

1. Once the script can successfully connect to the two databases, and has command line execution rights, you should be able to run it as a shell command: **./migrate.py**
2. Depending on your machine, the process may run for upwards of 15 minutes. (Sorry, I didn't get around to optimising/consolidating the many queries into something more efficient with JOINs etc.)
3. When it's done, your Live DB will have been modified. I have been using mysqldump to export the updated Live into an .SQL file.
4. I then upload (via scp) and import that .SQL file into the Test Migration environment, using WP CLI import {dumpname}.
5. Post-import cleanup (below)

# Post-import cleanup

The following WordPress front-end widget will remain after import:

* You'll want to import ACF using the export .json (provided here in /json/)
* Home's ACF widgets need to have their categories and posts set -- been doing this manually.
* Main and footer menus (due to caution in not wanting to break taxonomies with products in them) need to be set up after export.
* Category Images need to have their GUIDs search-and-replaced (in wp_options) to point to the correct server.
* Other wp_options should be search-and-replaced to indicate new site URL.

# Other notes

* You can configure things like which keys and CPTs are affected, under Config.yaml.
* Former Post IDs of posts that have been remapped can be found under the wp_postmeta key "old_id".

