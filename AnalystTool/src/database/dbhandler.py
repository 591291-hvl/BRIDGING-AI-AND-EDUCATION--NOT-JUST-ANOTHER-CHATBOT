from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import os
from src.database import chatDatabase
from src.database import analysisDatabase
from src import CustomizedCalendar
from datetime import datetime, timedelta
import json

load_dotenv()

class DBhandler:
    def __init__(self):
        self.WEEK = CustomizedCalendar.WEEKDAY
        self.calender = CustomizedCalendar.CustomizedCalendar(start_weekday=self.WEEK.MON, indicator_weekday=self.WEEK.SAT)
        self.chatURI = os.getenv("chatdb")
        self.chatClient = MongoClient(self.chatURI, server_api=ServerApi('1'))['chat-ui']
        self.analysisURI = os.getenv("teachertooldb")
        self.analysisClient = MongoClient(self.analysisURI, server_api=ServerApi('1'))['MSC01']

    def chatDatabaseClient(self):
        return self.chatClient

    def analysisDatabaseClient(self):
        return self.analysisClient

    def getNumberOfUsers(self):
        return chatDatabase.getNumberOfUsers(self.chatDatabaseClient())

    def getNumberOfNewUsersThisWeek(self, timestamp):
        startOfWeek = self.calender.getStartOfWeek(timestamp)
        endOfWeek = self.calender.getEndOfWeek(timestamp)
        return chatDatabase.getNumberOfNewUsersThisWeek(self.chatDatabaseClient(), startOfWeek, endOfWeek)

    def getNumberOfActiveUsersThisWeek(self, startOfCourseTimeStamp, timestamp):
        startOfWeek = self.calender.getStartOfWeek(timestamp)
        endOfWeek = self.calender.getEndOfWeek(timestamp)
        return chatDatabase.activeUsersThisWeek(self.chatDatabaseClient(),startOfCourseTimeStamp, timestamp, self.calender)


    def getNumberOfMessagesThisWeek(self, timestamp):
        startOfWeek = self.calender.getStartOfWeek(timestamp)
        endOfWeek = self.calender.getEndOfWeek(timestamp)
        return chatDatabase.getNumberOfMessagesThisWeek(self.chatDatabaseClient(), startOfWeek, endOfWeek)


    def getAllConversations(self, timestamp):
        startOfWeek = self.calender.getStartOfWeek(timestamp)
        endOfWeek = self.calender.getEndOfWeek(timestamp)
        return chatDatabase.getConversationsThisWeek(self.chatDatabaseClient(),startOfWeek, endOfWeek)

    def getWeeklyReport(self): #TODO FIND BETTER PLACE FOR THIS, SAME CODE EXISTS IN FORMATER
        with open("src/json/weeklyreport.json", "r", encoding="utf-8") as file:
            weeklyReport = file.read()
        weeklyReportJson = json.loads(weeklyReport)
        return weeklyReportJson

    def initWeeklyReport(self, dateNow):
        thisWeek = self.calender.calculate(dateNow)[1]

        collections = self.analysisClient["weeklyReport" + str(thisWeek)]
        collections.insert_one(self.getWeeklyReport())

    def getWeeklyReportCollection(self, dateNow):
        thisWeek = self.calender.calculate(dateNow)[1]
        if not "weeklyReport" + str(thisWeek) in self.analysisClient.list_collection_names():
            self.initWeeklyReport(dateNow)
        collection = self.analysisClient["weeklyReport" + str(thisWeek)]

        return collection

    def getMainWeeklyReportCollection(self):
        return analysisDatabase.getMainWeeklyReportCollection()

    def getMainWeeklyReport(self):
        return analysisDatabase.getWeeklyReport()

    def getWeeklyReportByNumber(self, weekNumber):
        return analysisDatabase.getWeeklyReportByNumber(weekNumber)


    def moveWeeklyReportToMainReport(self, weeklyReportCollection, dateNow):
        weeklyReport = weeklyReportCollection.find_one()
        if not "weeklyReport" in self.analysisClient.list_collection_names():
            analysisDatabase.createCollection("weeklyReport")
        mainCollection = self.getMainWeeklyReportCollection()
        if mainCollection.count_documents({}) == 0:
            analysisDatabase.addItemWithCollection(weeklyReport, mainCollection)
        else:
            analysisDatabase.updateItem(weeklyReport, mainCollection)

    def saveWeeklyReport(self, weeklyReport, timestamp):

        weeklyReportCollection = self.getWeeklyReportCollection(timestamp)

        analysisDatabase.updateItem(weeklyReport, weeklyReportCollection)

        self.moveWeeklyReportToMainReport(weeklyReportCollection, timestamp)

        return

    def getPastWeeklyReportCollection(self, weekList):
        return analysisDatabase.getPastWeeklyReportCollections(weekList)

    def getPastWeeklyReports(self, listOfWeeklyReportCollections):
        return analysisDatabase.getPastWeeklyReports(listOfWeeklyReportCollections)

    def updateTrends(self, trendList):


        for week in trendList:
            filter_query = {"Week": week['Week']}
            analysisDatabase.updateTrend(week, filter_query)

        return


    def getWeeklyChange(self):
        return analysisDatabase.getWeeklyChange()

    def updateWeeklyChange(self, content):
        return analysisDatabase.weeklyChange(content)

    def getSummary(self):
        return analysisDatabase.getSummary()


    def updateSummary(self, content):
        return analysisDatabase.updateSummary(content)


















