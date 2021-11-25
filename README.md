# Visible Import SQL Migration Script

# Overview
This is a Python command line script that reconciles two locally-run databases, Live and Production.

# Setup

You will need:
* Python 3
* A MySQL or MariaDB server with the two source databases imported.

To configure the script to connect with the two databases, you will need to enter credentials for a DB user into the config file, Config.yaml. (The user will also need to be granted all access privileges in SQL, of course.) Otherwise you will get an ACCESS_DENIED error.

To output a log file instead of printing to the screen, you can set Logging to True in the main file, which is Migrate.py.


# Use

1. Once the script can connect, you should be able to run it, assuming it has execution rights, by executing it as a shell command: **./migrate.py**
2. Depending on your machine, it may run for upwards of 15 minutes as I didn't get around to optimising/consolidating the many queries.
3. When it's done, your Live DB will have been modified. I have been using mysqldump to export it into an .SQL file.
4. I then import that .SQL file into the Test Migration environment, using WP CLI.


# Other notes

* You can configure things like which keys and CPTs are affected, under Config.yaml.
* Former Post IDs of posts that have been remapped can be found under the wp_postmeta key "old_id".


