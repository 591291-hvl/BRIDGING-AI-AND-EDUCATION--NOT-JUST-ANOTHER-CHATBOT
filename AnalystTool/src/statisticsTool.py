from src.utility.counter import Counter
from src.database.dbhandler import DBhandler
from src.utility.formatter import Formatter
from src import CustomizedCalendar
import json
from datetime import datetime, timedelta
from collections import defaultdict

#Responsible for gathering statistics for the weekly report, i.e how many new user, top 5 topics, etc. 

class StatisticTool:
    def __init__(self):
        self.WEEK = CustomizedCalendar.WEEKDAY
        self.calender = CustomizedCalendar.CustomizedCalendar(start_weekday=self.WEEK.MON, indicator_weekday=self.WEEK.SAT)
        self.counter = Counter()
        self.db = DBhandler()
        self.formatter = Formatter()

    def getTopics(self):
        with open("src/json/topics.json", "r", encoding="utf-8") as file:
            topicList = file.read()
        topicJson = json.loads(topicList)
        return [x['topic'] for x in topicJson['topics']]

    def getModules(self):
        with open("src/json/modules.json", "r", encoding="utf-8") as file:
            moduleList = file.read()
        moduleJson = json.loads(moduleList)
        return [x['name'] for x in moduleJson['modules']]

    def getUsage(self):
        with open("src/json/areaofuse.json", "r", encoding="utf-8") as file:
            usageList = file.read()
        usageJson = json.loads(usageList)
        return usageJson


    def runStatistics(self, topicsAndQuestions, modules, usage, startOfCourseTimeStamp, timestamp):

        statisticsJson = {}

        statisticsJson['Week'] = self.calender.calculate(timestamp)[1]

        statisticsJson['NumberOfQuestionsThisWeek'] = self.db.getNumberOfMessagesThisWeek(timestamp)
        statisticsJson['NumberOfConversationsThisWeek'] = len(self.db.getAllConversations(timestamp)) #Can reduce db call by counting this another place
        statisticsJson['NumberOfActiveUsersThisWeek'] = self.db.getNumberOfActiveUsersThisWeek(startOfCourseTimeStamp, timestamp)[-1][1]
        #print(statisticsJson['NumberOfActiveUsersThisWeek'])
        statisticsJson['NumberOfNewUsersThisWeek'] = self.db.getNumberOfNewUsersThisWeek(timestamp)

        statisticsJson['NonCodingQuestionsThisWeek'], statisticsJson['CodingQuestionsThisWeek'] = self.counter.codingRatio(usage)

        statisticsJson['TopicBreakdown'] = self.counter.countTopicsFromTopicsAndQuestions(topicsAndQuestions, self.getTopics())
        statisticsJson['ModuleBreakdown'] = self.counter.countModul(modules, self.getModules())
        statisticsJson['AreaOfUse'] = self.counter.countUsage(usage, self.getUsage())

        #Heatmap
        statisticsJson['Messages Day HeatMap'] = self.counter.hourInDayHeatMap(topicsAndQuestions)
        statisticsJson['Messages Week HeatMap'] = self.counter.dayInWeekHeatMap(topicsAndQuestions)
        return statisticsJson

    #Returns list containing the questions that should be aggregated
    def getQuestionsToAggregate(self, topicsAndQuestions, topicBreakdown):
        top_5_lambda = sorted(topicBreakdown, key=lambda x: x[1], reverse=True)[:5]
        top_5_topics = [item[0] for item in top_5_lambda]
        topic_dict = defaultdict(list)

        for item in topicsAndQuestions:
            for q in item["questions"]:
                if q["topic"] in top_5_topics:
                    topic_dict[q["topic"]].append(q["question"])

            # Merge questions into single strings
        merged_questions = [" ".join(questions) for questions in topic_dict.values()]
        return merged_questions

    def listOfWeeks(self, startDate, endDate):
        numberOfWeeks = (endDate - startDate).days // 7 + 1

        weekNumberList = []
        date = startDate

        for i in range(numberOfWeeks):
            weekNumber = self.calender.calculate(date)
            weekNumberList.append(weekNumber[1])
            date = date + timedelta(days=7)
        return weekNumberList

    def getWeeklyReportCollections(self, weekList):
        return self.db.getPastWeeklyReportCollection(weekList)

    def getPastWeeklyReports(self, listOfWeeklyReportCollections):
        return self.db.getPastWeeklyReports(listOfWeeklyReportCollections)

    def runTrends(self, startOfCourseTimeStamp, timestamp):

        listOfWeeks = self.listOfWeeks(startOfCourseTimeStamp, timestamp)
        listOfWeeklyReportCollections = self.getWeeklyReportCollections(listOfWeeks)
        pastWeeklyReportList = self.getPastWeeklyReports(listOfWeeklyReportCollections)
        activeUsers = self.db.getNumberOfActiveUsersThisWeek(startOfCourseTimeStamp, timestamp)
        trendList = self.formatter.formatIntoTrends(pastWeeklyReportList, activeUsers)
        self.db.updateTrends(trendList)

        return