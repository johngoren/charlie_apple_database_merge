import yaml
import mysql.connector
import pdb

with open("config.yaml", "r") as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

stagingDb = mysql.connector.connect(
        host=config["STAGING"]["host"],
        user=config["STAGING"]["user"],
        password=config["STAGING"]["password"],
        database=config["STAGING"]["database"]
    )

liveDb = mysql.connector.connect(
        host=config["LIVE"]["host"],
        user=config["LIVE"]["user"],
        password=config["LIVE"]["password"],
        database=config["LIVE"]["database"]
)

staging = stagingDb.cursor(dictionary=True, buffered=True)

live = liveDb.cursor(dictionary=True, buffered=True)

dont_bring_these_product_keys_over_from_staging = config["STAGING"]["omit_keys"]
dont_bring_these_post_types_over_from_staging = config["STAGING"]["omit_types"]
dont_bring_these_tables_over_from_staging = config["STAGING"]["omit_tables"]
preserve_these_keys_on_live = config["LIVE"]["preserve_keys"]
copy_these_tables = config["STAGING"]["copy_tables"]
siteurl = config["LIVE"]["url"]
