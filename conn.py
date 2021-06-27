import mysql.connector as sql
import config

def connect():
    return sql.connect(
            user = config.user,
            host = config.host,
            password = config.password,
            database = config.dbname)

