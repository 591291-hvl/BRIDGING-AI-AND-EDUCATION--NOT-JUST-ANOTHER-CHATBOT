from collections import Counter as counter
from datetime import datetime, timedelta


class Counter:
    def __init__(self):
        pass


    def countTopicsFromTopicsAndQuestions(self, topicsQuestionsJson, topicsList):
        topicsFromUsers = counter([questions["topic"] for conversation in topicsQuestionsJson for questions in
                           conversation["questions"]])
        topicList = []
        for topic in topicsList:
            topicList.append((topic, 0))

        return [(topic, topicsFromUsers.get(topic, 0)) for topic, _ in topicList]


    def countModul(self, questionModuleList, moduleList):
        modulesFromUsers = counter([module["name"] for conversation in questionModuleList for module in
                                   conversation["module"]])
        modulesList = []
        for module in moduleList:
            modulesList.append((module, 0))

        return [(module, modulesFromUsers.get(module, 0)) for module, _ in modulesList]

    def countUsage(self, questionUsageList, usageList):
        usageFromUsers = counter([usages["category"] for conversation in questionUsageList for usages in
                                    conversation["usage"]])

        usageList['Area Of Use']['Course Related']['Quizzing'] = usageFromUsers.get("Quizzing", 0)
        usageList['Area Of Use']['Course Related']['Course Topics Questions'] = usageFromUsers.get("Course Topics Questions", 0)
        usageList['Area Of Use']['Course Related']['Project Work'] = usageFromUsers.get("Project Work", 0)
        usageList['Area Of Use']['Course Related']['Course Formality Questions'] = usageFromUsers.get("Course Formality Questions", 0)
        usageList['Area Of Use']['Course Related']['Coding Questions'] = usageFromUsers.get("Coding Questions", 0)

        usageList['Area Of Use']['Other']['Other'] = usageFromUsers.get("Other", 0)

        return usageList

    def codingRatio(self, usageList):
        usageFromUsers = counter([usages["category"] for conversation in usageList for usages in conversation["usage"]])

        return sum(usageFromUsers.values()) - usageFromUsers.get("Coding Questions", 0), usageFromUsers.get("Coding Questions", 0)


    def hourInDayHeatMap(self, messages):
        hourDict = {i: 0 for i in range(24)}

        for conversations in messages:
            for questions in conversations['questions']:
                date = str(questions['timestamp'])
                if "." not in date:
                    date += ".000000"
                hourDict[datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f").time().hour] += 1

        hourList = [(k, hourDict.get(k)) for k in hourDict.keys()]
        return hourList

    def dayInWeekHeatMap(self, messages):

        dayDict = {i: 0 for i in range(7)}
        for conversation in messages:
            for questions in conversation['questions']:
                date = str(questions['timestamp'])
                #print(date)
                if "." not in date:
                    date += ".000000"
                dayDict[datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f").weekday()] += 1
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return [(days_of_week[(k+0)%7], dayDict.get((k+0)%7), str(0) + str(k) + "-" + days_of_week[(k+0)%7]) for k in dayDict.keys()]


