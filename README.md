# Visible Import SQL Migration Script

# Overview
This is a Python command line script that reconciles two locally-run databases, Live and Production.

# Setup

You will need:
* Python 3
* A MySQL or MariaDB server with the two source databases imported.

To configure the script to connect with the two databases, you will need to enter credentials for a DB user into the config file, Config.yaml. (The user will also need to be granted all access privileges in SQL, of course.) Otherwise you will run into an ACCESS_DENIED error.

To output a log file instead of printing to the screen, you can set Logging to True in the main file, which is Migrate.py.


# Use

1. Once the script can connect, you should be able to run it, assuming it has execution rights, by executing it as a shell command: **./migrate.py**
2. Depending on your machine, it may run for upwards of 15 minutes. (Sorry, I didn't get around to optimising/consolidating the many queries into something faster)
3. When it's done, your Live DB will have been modified. I have been using mysqldump to export it into an .SQL file.
4. I then import that .SQL file into the Test Migration environment, using WP CLI.

# Post-import cleanup

The following issues have been persisting after import:

* ACF can be imported using the export .json (available here in /json/)
* Home's ACF widgets need to have their categories and posts set -- been doing this manually.
* Main and footer menus (due to caution in not wanting to break taxonomies with products in them) need to be set up after export.
* Category Images need to have their GUIDs search-and-replaced (in wp_options) to point to the correct server.
* Other wp_options should be search-and-replaced to indicate new site URL.

# Other notes

* You can configure things like which keys and CPTs are affected, under Config.yaml.
* Former Post IDs of posts that have been remapped can be found under the wp_postmeta key "old_id".

