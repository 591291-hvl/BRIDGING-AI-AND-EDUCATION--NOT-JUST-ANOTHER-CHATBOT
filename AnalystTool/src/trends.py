from datetime import datetime, timedelta
from enum import IntEnum
import CustomizedCalendar
import os
from dotenv import load_dotenv
from pymongo import MongoClient, DESCENDING
from pymongo.server_api import ServerApi
from database import analysisDatabase

load_dotenv(dotenv_path="../.env")

uri = os.getenv("teachertooldb")
db = MongoClient(uri, server_api=ServerApi('1')).MSC01

WEEKDAY = IntEnum('WEEKDAY', 'MON TUE WED THU FRI SAT SUN', start=1)


WEEK = CustomizedCalendar.WEEKDAY
my_calendar = CustomizedCalendar.CustomizedCalendar(start_weekday=WEEK.WED, indicator_weekday=WEEK.MON)


def listOfWeeks(startDate, endDate):
    numberOfWeeks = (endDate - startDate).days//7 + 1

    weekNumberList = []
    date = startDate

    for i in range(numberOfWeeks):
        weekNumber = my_calendar.calculate(date)
        weekNumberList.append(weekNumber[1])
        date = date + timedelta(days=7)
    return weekNumberList

def getCollections(startDate, endDate):
    weekNumberList = listOfWeeks(startDate, endDate)
    collectionList = []
    for weekNumber in weekNumberList:
        collectionList.append(db["weeklyReport" + str(weekNumber)])

    return collectionList, weekNumberList

def updateTrends(startDate, endDate, hourInDayList, dayInWeekList, activeUsersList):
    collections, weekNumberList = getCollections(startDate, endDate)

    trendsCollection = db["trends"]


    trends = []
    for i in range(len(weekNumberList)):
        collection = collections[i]
        weeknumber = weekNumberList[i]
        filter_query = {"Week": weeknumber}
        document = collection.find_one()
        new_doc = {'Week':  document['Week'],
                   'Questions_This_Week': document['data'][0]['Engagement'][0]['Total_Questions_This_Week'],
                   'Conversations_This_Week': document['data'][0]['Engagement'][1]['Total_Conversation_This_Week'],
                   'New_Users': document['data'][0]['Engagement'][2]['New_Users_This_Week'],
                   'Hour_In_Day': hourInDayList,
                   'Days_In_Week': dayInWeekList,
                   'Active_Users': activeUsersList}
        trends.append(new_doc)
        #print(new_doc)
        trendsCollection.replace_one(filter_query, new_doc, upsert=True)




