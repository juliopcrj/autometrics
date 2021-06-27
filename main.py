import sys
import mysql.connector as sql
import gspread
from gspread.utils import a1_to_rowcol, rowcol_to_a1
from config import *
from queries import *

class Autometrics:

    sites_sheet = [ "CRIE-UNIFESP", "RIO - IDOR", "BAHIA - IDOR", "UFSM", "CPCLIN" ]
    general_sheet = "https://docs.google.com/spreadsheets/d/1TvXq18udAPxT52-SbcwXWLqYTjgXiqTtUp6tp5-vJIo/edit#gid=0"
    sites_ids = ['1', '2', '3', '4', '6']
    begin_date = "2021-06-27"
    date_query = 'select current_date() - interval 7 day, current_date() - interval 1 day'


    sheet = None
    editing_column = 0
    database = None
    cursor = None

    def __init__(self):
        try:
            database = sql.connect(
                    host = host,
                    user = user,
                    password = password,
                    database = dbname
                    )
        except:
            sys.exit("Couldn't connect to the database, please review your config file")

        # This block is just to retrieve the column in which the data should be written
        cursor = database.cursor()
        cursor.execute("select timestampdiff(day, date("+begin_date+"), current_date())")
        result = cursor.fetchone()
        days = result[0]
        week = days//7
        editing_column = gspread.utils.a1_to_rowcol("AF4")[1] + week

        # Now get the sheet to update
        gc = gspread.service_account()
        sheet = gc.open_by_url(general_sheet)


    def close(self):
        database.close()


    def run(self):
        participants = participants.replace("\n", " ")
        reports = reports.replace("\n", " ")
        installed = installed.replace("\n", " ")
        churn = churn.replace("\n", " ")
        positive = positive.replace("\n", " ")

        for i in range(5):
            worksheet = sheet.worksheet(sites_sheet[i])
            _participants = participants.replace("<SITE_ID>", sites_ids[i])
            _reports = reports.replace("<SITE_ID>", sites_ids[i])
            _installed = installed.replace("<SITE_ID>", sites_ids[i])
            _churn = churn.replace("<SITE_ID>", sites_ids[i])
            _positive = positive.replace("<SITE_ID>", sites_ids[i])


            # Sets the date
            cursor.execute(date_query)
            _data = cursor.fetchone()
            _data = str(_data[0]) + "-" + str(_data[1])
            worksheet.update_cell(4, editing_column, _data)
            worksheet.format(gspread.utils.rowcol_to_a1(4, editing_column), {'textFormat':{'bold':True}})

            # begins fetching and writing the new data
            cursor.execute(_participants)
            res = cursor.fetchone()
            worksheet.update_cell(5, editing_column, res[0])

            cursor.execute(_installed)
            res = cursor.fetchone()
            worksheet.update_cell(6, editing_column, res[0])

            cursor.execute(_churn)
            res = cursor.fetchone()
            worksheet.update_cell(9, editing_column, res[0])

            cursor.execute(_positive)
            res = cursor.fetchone()
            worksheet.update_cell(11, editing_column, res[0])

            cursor.execute(_reports)
            res = cursor.fetchone()
            worksheet.update_cell(12, editing_column, res[0])
            # end of fetch and write new data

            # writes the formulas
            worksheet.update(rowcol_to_a1(7, editing_column), "="+rowcol_to_a1(12, editing_column)+"/"+rowcol_to_a1(6, editing_column), raw=False)
            worksheet.update(rowcol_to_a1(8, editing_column), "="+rowcol_to_a1(6, editing_column) +"/"+rowcol_to_a1(5,editing_column), raw=False)
            worksheet.update(rowcol_to_a1(10,editing_column), "="+rowcol_to_a1(6,editing_column)+"-"+rowcol_to_a1(6,editing_column-1), raw=False)
            worksheet.update(rowcol_to_a1(13,editing_column),
                    "=("+rowcol_to_a1(12, editing_column) + "-" +rowcol_to_a1(11, editing_column) +")/"+rowcol_to_a1(12,editing_column),raw=False)


        self.close()

if __name__ == "__main__":
    pfs = Autometrics()
    pfs.run()
