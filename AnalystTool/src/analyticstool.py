from src.LLM.gpt import GPT
from src.database.dbhandler import DBhandler
from src.utility.extractor import Extractor
from src.utility.formatter import Formatter
from src.statisticsTool import StatisticTool
from src.utility.timehandler import getLastWeekWeekNumber, getTimeNow
from datetime import datetime, timedelta

class AnalyticsTools:
    def __init__(self):
        self.gpt = GPT()
        self.dbhandler = DBhandler()
        self.extractor = Extractor()
        self.formatter = Formatter()
        self.statisticsTool = StatisticTool()

    
    def sumUpWeekly(self):
        weeklyReport = self.dbhandler.getMainWeeklyReport()
        formattedWeeklyReport = str(weeklyReport)
        return self.dbhandler.updateSummary(self.gpt.sumUpWeekly(formattedWeeklyReport))

    def getSummary(self):
        return self.dbhandler.getSummary()['Summary'] #'Summary' if for only getting the "content", use 'LastUpdated' for date check

    def weeklyChange(self, timestamp):
        lastWeekNumber = getLastWeekWeekNumber(timestamp)
        weeklyReport = str(self.dbhandler.getMainWeeklyReport())
        lastWeeksReport = str(self.dbhandler.getWeeklyReportByNumber(lastWeekNumber))
        #print(weeklyReport)
        #print(lastWeeksReport)
        return self.dbhandler.updateWeeklyChange(self.gpt.weeklyChange(weeklyReport, lastWeeksReport))

    def getWeeklyChange(self):
        return self.dbhandler.getWeeklyChange()['weeklyChange']

    def getAggregate(self):
        weeklyReport = self.dbhandler.getMainWeeklyReport()
        date = weeklyReport['LastUpdated'] #TODO logic for redo weeklyreport
        questions = weeklyReport['data']['Aggregated Questions']
        returnHTML = "<ul>" + "\n"
        for question in questions:
            returnHTML += "  <li>" + question + "</li>" + "\n"
        returnHTML += "</ul>"
        return returnHTML
        #If dbhandler.getWeeklyReport() != None:
        # return Weekly.aggregate
        #else:
        #weeklyreport(startOfCourseTimeStamp, timestamp)
        #return Weekly.aggregate

    def weeklyReport(self, startOfCourseTimeStamp, timestamp):
        #Get all conversations from the database thats relevant to the week of the timestamp 
        conversations = self.dbhandler.getAllConversations(timestamp)
        #print([[i['createdAt'] for i in x['messages']] for x in conversations])
        #Prep for statistics
        topicsAndQuestions = []
        modules = []
        usage = []


        # Run through each conversation and do classification 
        for conversation in conversations:

            #Extract the conversation and format
            extracted_conversation = self.extractor.extract_fields(conversation)
            formatted_conversation = self.formatter.jsonToString(extracted_conversation)

            #Classify the conversation
            topicsAndQuestions.append(self.gpt.classifyTopics(formatted_conversation))
            modules.append(self.gpt.classifyModule(formatted_conversation)) 
            usage.append(self.gpt.classifyAreaOfUse(formatted_conversation))

        #Remove chat messages that are not from this week
        topicsAndQuestions = self.formatter.removeNotThisWeekTopic(topicsAndQuestions, timestamp)
        modules = self.formatter.removeNotThisWeekModules(modules, timestamp)
        usage = self.formatter.removeNotThisWeekUsage(usage, timestamp)



        #Run statistics
        #print(topicsAndQuestions, modules, usage)
        statistic = self.statisticsTool.runStatistics(topicsAndQuestions, modules, usage,startOfCourseTimeStamp, timestamp)

        questionList = self.statisticsTool.getQuestionsToAggregate(topicsAndQuestions, statistic['TopicBreakdown'])
        #print(questionList)
        #Aggregate the questions
        aggregatedQuestions = []
        for questions in questionList:
            aggregatedQuestions.append(self.gpt.aggregateQuestion(questions))
        #print(aggregatedQuestions)
        #Format the weekly report
        weeklyReport = self.formatter.formatWeekly(statistic, aggregatedQuestions)
        #Save the weekly report
        self.dbhandler.saveWeeklyReport(weeklyReport, timestamp)
    
        #update trends
        self.trends(startOfCourseTimeStamp, timestamp)

        #update summary
        self.sumUpWeekly()

        #update weekly change
        self.weeklyChange(timestamp)


    def trends(self, startOfCourseTimeStamp, timestamp):

        self.statisticsTool.runTrends(startOfCourseTimeStamp, timestamp)

        pass



#a = AnalyticsTools()
#a.weeklyReport(datetime(2025, 1, 27), datetime(2025, 5, 25, 23, 59, 59, 999999))
#a.weeklyReport(datetime(2025, 1, 27), datetime.now())
#print(a.getAggregate())
