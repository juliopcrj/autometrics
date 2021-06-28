import sys
import mysql.connector as sql
import gspread
from gspread.utils import a1_to_rowcol, rowcol_to_a1
from config import *
import queries

sites_sheet = [ "CRIE-UNIFESP", "CPCLIN", "RIO - IDOR", "UFSM", "BAHIA - IDOR" ]
general_sheet = "https://docs.google.com/spreadsheets/d/1TvXq18udAPxT52-SbcwXWLqYTjgXiqTtUp6tp5-vJIo/edit#gid=0"
sites_ids = ['1', '2', '3', '5', '4']
begin_date = "2021-06-27"
date_query = 'select current_date() - interval 7 day, current_date() - interval 1 day'



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

        # This block is just to retrieve the column in which the data should be written
        self.cursor = self.database.cursor()
        self.cursor.execute("select timestampdiff(week, \""+begin_date+"\", current_date());")
        result = self.cursor.fetchone()
        week = result[0]
        self.editing_column = gspread.utils.a1_to_rowcol("AF4")[1] + week

        # Now get the self.sheet to update
        gc = gspread.service_account()
        self.sheet = gc.open_by_url(general_sheet)


    def close(self):
        self.database.close()


    def run(self):
        participants = queries.participants.replace("\n", " ")
        reports = queries.reports.replace("\n", " ")
        installed = queries.installed.replace("\n", " ")
        churn = queries.churn.replace("\n", " ")
        positive = queries.positive.replace("\n", " ")

        self.cursor.execute(date_query)
        _data = self.cursor.fetchone()
        _inicio = str(_data[0]).split("-")
        _inicio = "/".join([_inicio[2], _inicio[1], _inicio[0]])
        _fim = str(_data[1]).split("-")
        _fim = "/".join([_fim[2], _fim[1], _fim[0]])
        _data = _inicio + "-" + _fim

        for i in range(5):
            worksheet = self.sheet.worksheet(sites_sheet[i])
            _participants = participants.replace("<SITE_ID>", sites_ids[i])
            _reports = reports.replace("<SITE_ID>", sites_ids[i])
            _installed = installed.replace("<SITE_ID>", sites_ids[i])
            _churn = churn.replace("<SITE_ID>", sites_ids[i])
            _positive = positive.replace("<SITE_ID>", sites_ids[i])


            # Sets the date
            worksheet.update_cell(4, self.editing_column, _data)
            worksheet.format(gspread.utils.rowcol_to_a1(4, self.editing_column), {'textFormat':{'bold':True}})

            # begins fetching and writing the new data
            self.cursor.execute(_participants)
            res = self.cursor.fetchone()
            worksheet.update_cell(5, self.editing_column, res[0])

            self.cursor.execute(_installed)
            res = self.cursor.fetchone()
            worksheet.update_cell(6, self.editing_column, res[0])

            self.cursor.execute(_churn)
            res = self.cursor.fetchone()
            worksheet.update_cell(9, self.editing_column, res[0])

            self.cursor.execute(_positive)
            res = self.cursor.fetchone()
            worksheet.update_cell(11, self.editing_column, res[0])

            self.cursor.execute(_reports)
            res = self.cursor.fetchone()
            worksheet.update_cell(12, self.editing_column, res[0])
            # end of fetch and write new data

            # writes the formulas
            worksheet.update(rowcol_to_a1(7, self.editing_column), "="+rowcol_to_a1(12, self.editing_column)+"/"+rowcol_to_a1(6, self.editing_column), raw=False)
            worksheet.update(rowcol_to_a1(8, self.editing_column), "="+rowcol_to_a1(6, self.editing_column) +"/"+rowcol_to_a1(5,self.editing_column), raw=False)
            worksheet.update(rowcol_to_a1(10,self.editing_column), "="+rowcol_to_a1(6,self.editing_column)+"-"+rowcol_to_a1(6,self.editing_column-1), raw=False)
            worksheet.update(rowcol_to_a1(13,self.editing_column),
                    "=("+rowcol_to_a1(12, self.editing_column) + "-" +rowcol_to_a1(11, self.editing_column) +")/"+rowcol_to_a1(12,self.editing_column),raw=False)


        self.close()

if __name__ == "__main__":
    pfs = Autometrics()
    pfs.run()
