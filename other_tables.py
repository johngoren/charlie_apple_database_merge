import dbs
import pdb

# Potentially use sql alchemy https://stackoverflow.com/questions/46942301/copy-tables-from-one-database-to-another-in-sql-server-using-python

def copy():
    for table in dbs.copy_these_tables:
        # select * from table
        print("TODO copy other tables")