import json
from datetime import datetime, timedelta
from src import CustomizedCalendar

class Formatter:

    def __init__(self):
        self.WEEK = CustomizedCalendar.WEEKDAY
        self.calender = CustomizedCalendar.CustomizedCalendar(start_weekday=self.WEEK.MON, indicator_weekday=self.WEEK.SAT)

    def getWeeklyReport(self):
        with open("src/json/weeklyreport.json", "r", encoding="utf-8") as file:
            weeklyReport = file.read()
        weeklyReportJson = json.loads(weeklyReport)
        return weeklyReportJson

    def formatWeekly(self, statistic, aggregatedQuestions):

        weeklyReport = self.getWeeklyReport()

        weeklyReport['Week'] = statistic['Week']

        weeklyReport['data']['Engagement']['Total Questions This Week'] = statistic['NumberOfQuestionsThisWeek']
        weeklyReport['data']['Engagement']['Total Conversation This Week'] = statistic['NumberOfConversationsThisWeek']
        weeklyReport['data']['Engagement']['Active Users This Week'] = statistic['NumberOfActiveUsersThisWeek']
        weeklyReport['data']['Engagement']['New Users This Week'] = statistic['NumberOfNewUsersThisWeek']

        weeklyReport['data']['Coding Non/Coding Ratio']['Total Coding Questions This Week'] = statistic['CodingQuestionsThisWeek']
        weeklyReport['data']['Coding Non/Coding Ratio']['Total NonCoding Questions This_Week'] = statistic['NonCodingQuestionsThisWeek']

        weeklyReport['data']['Topics'] = statistic['TopicBreakdown']
        weeklyReport['data']['Module Breakdown'] = statistic['ModuleBreakdown']
        weeklyReport['data']['Area Of Use'] = statistic['AreaOfUse']

        weeklyReport['data']['Messages Day HeatMap'] = statistic['Messages Day HeatMap']
        weeklyReport['data']['Messages Week HeatMap'] = statistic['Messages Week HeatMap']
        weeklyReport['data']['Aggregated Questions'] = aggregatedQuestions



        return weeklyReport
    
    def jsonToString(self,conversation):
        return json.dumps(conversation)

    def removeNotThisWeekTopic(self, content, timestamp):
        startOfWeek = self.calender.getStartOfWeek(timestamp)
        for i in range(len(content)):
            questions = []
            #print(content)
            for question in content[i]['questions']:
                date = str(question['timestamp'])
                try:
                    date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%f')
                except ValueError:
                    date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
                if date >= startOfWeek:
                    #print(date)
                    questions.append(question)
            content[i]['questions'] = questions
        return content

    def removeNotThisWeekModules(self, content, timestamp):
        startOfWeek = self.calender.getStartOfWeek(timestamp)
        for i in range(len(content)):
            modules = []
            for module in content[i]['module']:
                date = str(module['timestamp'])
                try:
                    date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%f')
                except ValueError:
                    date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
                if date >= startOfWeek:
                    modules.append(module)
            content[i]['module'] = modules
        return content

    def removeNotThisWeekUsage(self, content, timestamp):
        startOfWeek = self.calender.getStartOfWeek(timestamp)
        for i in range(len(content)):
            usages = []
            for usage in content[i]['usage']:
                date = str(usage['timestamp'])
                try:
                    date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%f')
                except ValueError:
                    date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
                if date >= startOfWeek:
                    usages.append(usage)
            content[i]['usage'] = usages
        return content

    def formatIntoTrends(self, pastWeeklyReportList, activeUsers):
        trendsList = []

        for weeklyReport in pastWeeklyReportList:
            trendsJson = {
                'Week': weeklyReport['Week'],
                'Questions_This_Week': weeklyReport['data']['Engagement']['Total Questions This Week'],
                'Conversations_This_Week': weeklyReport['data']['Engagement']['Total Conversation This Week'],
                'New_Users': weeklyReport['data']['Engagement']['New Users This Week'],
                'Active_Users': activeUsers,
                'Hour_In_Day': weeklyReport['data']['Messages Day HeatMap'],
                'Days_In_Week': weeklyReport['data']['Messages Week HeatMap']
            }
            trendsList.append(trendsJson)

        return trendsList