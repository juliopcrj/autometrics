import sys
import mysql.connector as sql
import gspread
from gspread.utils import a1_to_rowcol, rowcol_to_a1
from config import *
import queries
from pushbullet import Pushbullet
from pb import key

sites_sheet = [ "CRIE-UNIFESP", "CPCLIN", "RIO - IDOR", "UFSM", "BAHIA - IDOR" ]
general_sheet = "https://docs.google.com/spreadsheets/d/1TvXq18udAPxT52-SbcwXWLqYTjgXiqTtUp6tp5-vJIo/edit#gid=0"
sites_ids = ['1', '2', '3', '5', '4']
begin_date = "2021-06-27"
date_query = 'select current_date() - interval 7 day, current_date() - interval 1 day'

participants_line = 5
installs_line = 6
churn_line = 11
positive_line = 13
report_line = 14

adherence_line = 9
newusers_line = 12
effort_line = 15
valid_line = 8
rate_installs_line = 10


class Autometrics:

    def __init__(self):
        self.pb = Pushbullet(key)

        try:
            self.database = sql.connect(
                    host = host,
                    user = user, 
                    password = password,
                    database = dbname
                    )
        except:
            _ = self.pb.push_note("Alert", "Nao executou autometrics")

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
            worksheet.update_cell(participants_line, self.editing_column, res[0])

            self.cursor.execute(_installed)
            res = self.cursor.fetchone()
            worksheet.update_cell(installs_line, self.editing_column, res[0])

            self.cursor.execute(_churn)
            res = self.cursor.fetchone()
            worksheet.update_cell(churn_line, self.editing_column, res[0])

            self.cursor.execute(_positive)
            res = self.cursor.fetchone()
            worksheet.update_cell(positive_line, self.editing_column, res[0])

            self.cursor.execute(_reports)
            res = self.cursor.fetchone()
            worksheet.update_cell(report_line, self.editing_column, res[0])
            # end of fetch and write new data

            # writes the formulas
            worksheet.update(rowcol_to_a1(adherence_line, self.editing_column), "="+rowcol_to_a1(report_line, self.editing_column)+"/"+rowcol_to_a1(participants_line, self.editing_column), raw=False)
            worksheet.update(rowcol_to_a1(rate_installs_line, self.editing_column), "="+rowcol_to_a1(installs_line, self.editing_column) +"/"+rowcol_to_a1(participants_line,self.editing_column), raw=False)
            worksheet.update(rowcol_to_a1(newusers_line,self.editing_column), "="+rowcol_to_a1(installs_line,self.editing_column)+"-"+rowcol_to_a1(installs_line,self.editing_column-1), raw=False)
            worksheet.update(rowcol_to_a1(effort_line,self.editing_column),
                    "=("+rowcol_to_a1(report_line, self.editing_column) + "-" +rowcol_to_a1(positive_line, self.editing_column) +")/"+rowcol_to_a1(report_line,self.editing_column),raw=False)


        _ = self.pb.push_note("Report", "Atualizou as métricas no COV003")
        self.close()

if __name__ == "__main__":
    pfs = Autometrics()
    pfs.run()
