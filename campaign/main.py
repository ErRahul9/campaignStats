import json
import re
from datetime import datetime

import pandas
import pandas as pd
import psycopg2
from dotenv import load_dotenv
import os
from sys import argv
import statsmodels.api as sm
import matplotlib.pyplot as plt
# import Jinja2



class main():
    def __init__(self):
        self.adv_id = argv[1]
        self.baseDate = argv[2]
        self.tgtDate = argv[3]
        load_dotenv()
        self.host = os.environ["CORE_HOST"]
        self.user = os.environ["CORE_USER"]
        self.pwd = os.environ["CORE_PW"]
        self.port = os.environ["CORE_PORT"]
        self.db = os.environ["CORE_DATABASE"]
        self.conn = psycopg2.connect(database=self.db, user=self.user, password=self.pwd, host=self.host, port=self.port)


    def readJson(self):
        returnJsonObjects = {}
        jsonPath = os.path.join(self.path, self.filename)
        readFile = json.load(open(jsonPath))
        for Key, values in readFile.items():
            returnJsonObjects[Key] = values
        return returnJsonObjects

    # def __init__(self):

    def returnData(self):
        sqlData = self.setQueryfromParameters()
        # sql = sqlData.get(query).lower()
        advsql = self.setAdvertiserId(sqlData)
        finalSQL = self.setStartEndDate(advsql)
        print(finalSQL)
        return  finalSQL


    def setAdvertiserId(self,sql):
        sqlUpdated = re.sub("\\d{5}",self.adv_id,sql)
        return sqlUpdated

    def setStartEndDate(self,updatedQuery):
        if "hour" in updatedQuery.lower():
            tTime = self.baseDate + " 00:00:00"
            eTime = self.tgtDate + " 00:00:00"
            updatedStartTime = re.sub(r">= '2023-02-22 00:00:00'",">= '{}'".format(tTime),updatedQuery)
            updateQueryTime = re.sub(r"< '2023-02-23 00:00:00'","< '{}'".format(eTime),updatedStartTime)
        elif "day" in updatedQuery.lower():
            updatedStartTime = re.sub(r">= '2023-02-22'", ">= '{}'".format(self.baseDate), updatedQuery)
            updateQueryTime = re.sub(r"< '2023-03-01'", "< '{}'".format(self.tgtDate), updatedStartTime)

        return updateQueryTime


    def setQueryfromParameters(self):
        sqlData = open("resources/campaign.sql",'r').read().lower()
        sqlWithAdv = self.setStartEndDate(self.setAdvertiserId(sqlData))
        return sqlWithAdv


    def report_generator(self):
        getResults = pandas.read_sql(main().returnData(),self.conn)
        getResults['winPercentage'] = (getResults['win_counts']/getResults['bids_counts'])*100
        getResults['Win_Percentage_average'] = getResults['winPercentage'].rolling(window=5).mean()
        report = getResults.style.set_table_styles([
            {'selector': 'th', 'props': [('background-color', '#4287f5'), ('color', 'white')]},
            {'selector': 'td', 'props': [('border', '1px solid black')]}
        ]).to_html()
        with open('report_{}.html'.format(self.tgtDate), 'w') as file:
            file.write(report)
        print("Report generated successfully!")
        plt.plot(getResults['bid_hour'], getResults['winPercentage'])
        plt.xlabel('bid_hour')
        plt.ylabel('winPercentage')
        plt.title('daily win percentage results')
        plt.savefig('plot_{}.png'.format(self.tgtDate))

if __name__ == '__main__':
    print(main().report_generator())
