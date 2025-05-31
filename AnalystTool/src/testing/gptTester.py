from src.LLM.gpt import GPT
from src.utility.extractor import Extractor
import json
from src.utility.formatter import Formatter

gpt = GPT()
extractor = Extractor()
formatter = Formatter()





def testClassifyer():
    with open('src/testing/testfiles/emptyconvo.json', "r", encoding="utf-8") as file:
        testconvo = json.loads(file.read())  # Convert string to dictionary
    conversation = json.dumps(extractor.extract_fields(testconvo))  # No more error
    print("Running GPT-4o on test conversation:")
    print("Module classification:")
    print(gpt.classifyModule(conversation))
    print("Area of use classification:")
    print(gpt.classifyAreaOfUse(conversation))
    print("Topic classification:")
    print(gpt.classifyTopics(conversation))

def testSumUp():
    with open('src/testing/testfiles/weeklyreport6.json', "r", encoding="utf-8") as file:
        weeklyReport = json.loads(file.read())  # Convert string to dictionary
    print("Running GPT-4o on weekly report:")
    print("Sum up weekly:")
    return (gpt.sumUpWeekly(formatter.jsonToString(weeklyReport)))

def testWeeklyChange():
    with open('src/testing/testfiles/weeklyreport5.json', "r", encoding="utf-8") as file:
        weeklyReport = json.loads(file.read())  # Convert string to dictionary
    with open('src/testing/testfiles/weeklyreport6.json', "r", encoding="utf-8") as file:
        lastWeeksReport = json.loads(file.read())  # Convert string to dictionary
    print("Running GPT-4o on weekly report:")
    print("Weekly change:")
    return (gpt.weeklyChange(formatter.jsonToString(weeklyReport), formatter.jsonToString(lastWeeksReport)))

def testAggregateQuestion():
    with open('src/testing/testfiles/questions.txt', "r", encoding="utf-8") as file:
        questions = file.read()  # Convert string to dictionary
    print("Running GPT-4o on questions:")
    print("Aggregate questions:")
    return gpt.aggregateQuestion(questions)




#print(testSumUp())
print(testWeeklyChange())