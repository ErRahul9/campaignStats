import json
import re
from datetime import datetime
from typing import io

import numpy as np
import pandas
from dotenv import load_dotenv
import os
from sys import argv
import statsmodels.api as sm
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from tabpy import tabpy
from tabpy.tabpy_tools import client
from tabpy.tabpy_tools.client import Client


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
        self.engine = create_engine("postgresql://{0}:{1}@{2}:{3}/{4}".format(self.user,self.pwd,self.host,self.port,self.db))
        # self.client = Client('http://localhost:9004/')

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
        getResults = pandas.read_sql(main().returnData(),self.engine)
        report = getResults.style.set_table_styles([
            {'selector': 'th', 'props': [('background-color', '#4287f5'), ('color', 'white')]},
            {'selector': 'td', 'props': [('border', '1px solid black')]}
        ]).to_html()
        with open('report_{}.html'.format(self.tgtDate), 'w') as file:
            file.write(report)
            # self.client.deploy('campaign chart ',report)
        print("Report generated successfully!")
        scale_factor = 2
        original_figsize = plt.rcParams["figure.figsize"]
        new_figsize = [size * scale_factor for size in original_figsize]
        plt.rcParams['figure.figsize'] = new_figsize

        fig, ax = plt.subplots()

        # ax.plot(getResults['bid_hour'], getResults['win_percentage'] , label='winPercentage',color='red')
        ax.plot(getResults['bid_hour'], getResults['avergae_bid_price'], label='average_bid_price',color='blue')
        ax.plot(getResults['bid_hour'], getResults['avergae_win_price'], label='average_win_price',color='green')
        ax.set_xlabel('hour')
        ax.set_ylabel('average counts')
        ax.set_title('Campaign performance')
        ax.legend()
        plt.savefig('plot_{}.png'.format(self.tgtDate))
        plt.show()
        # self.client.deploy('display campaign chart' , plt.show(),override=True)
        # image_bytes = io.BytesIO()
        # plt.savefig(image_bytes, format='png')
        # plt.close()
        # image_data = image_bytes.getvalue()
        # return image_data

        # bar_width = 0.2
        # x = np.arange(len(categories))
        # fig, ax = plt.subplots()
        #
        # rects1 = ax.bar(x , bid_hour, bar_width, label='bid_hour')
        # rects2 = ax.bar(x + bar_width, winPercentage, bar_width, label='winPercentage')
        # rects3 = ax.bar(x +2 * bar_width, avergae_bid_price, bar_width, label='avergae_bid_price')
        # rects4 = ax.bar(x + 4 * bar_width, avergae_win_price, bar_width, label='avergae_win_price')
        #
        # ax.set_xlabel('Categories')
        # ax.set_ylabel('Values')
        # ax.set_title('Graph Report with Campaign Stats')
        #
        # ax.set_xticks(x)
        # ax.set_xticklabels(categories)
        # ax.legend()
        # plt.show()

        # fig = plt.figure(figsize=(8, 6))
        # ax = fig.add_subplot(111, projection='3d')
        # # scatter = ax.scatter()
        # plt.plot(getResults['bid_hour'], getResults['winPercentage'])
        # scatter = ax.scatter('bid_hour','winPercentage','avergae_bid_price','avergae_win_price',cmap='viridis')
        # cbar = plt.colorbar(scatter)
        # plt.xlabel('avergae_bid_price')
        # plt.ylabel('avergae_win_price')
        # # plt.zlabel(getResults['avergae_bid_price'])
        # plt.title('daily win percentage results')
        # plt.savefig('plot_{}.png'.format(self.tgtDate))

        plt.show()
if __name__ == '__main__':
    print(main().report_generator())
