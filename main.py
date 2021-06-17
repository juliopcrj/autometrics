import sys
import mysql.connector as sql
import gspread
from oauth2client.service_account import ServiceAccountCredentials as SAC
from config import *
from queries import *

class Autometrics:

    def __init__(self):
        try:
            self.database = sql.connect(
                    host = host,
                    user = user,
                    password = password,
                    database = dbname
                    )
        except:
            sys.exit("Couldn't connect to the database, please review your config file")

    def __del__(self):
        print("Closing connection with database")
        self.database.close()


    def test(self):
        print(self.database)


    def run(self):
        pass

if __name__ == "__main__":
    Autometrics().test()

