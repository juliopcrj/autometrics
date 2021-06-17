import sys
import mysql.connector as sql
import gspread
from oauth2client.service_account import ServiceAccountCredentials as SAC
from config import *
from queries import *

class Autometrics:

    sites_sheet = ["", "", "", "", ""]
    sites_ids = ['1', '2', '3', '4', '6']

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
        self.close()

    def close(self):
        self.database.close()

    def test(self):
        print(self.database)


    def run(self):
        participants = participants.replace("\n", " ")
        reports = reports.replace("\n", " ")
        installed = installed.replace("\n", " ")
        churn = churn.replace("\n", " ")
        positive = positive.replace("\n", " ")
        

        for i in range(5):


if __name__ == "__main__":
    pfs = Autometrics()
    pfs.run()
    del pfs

