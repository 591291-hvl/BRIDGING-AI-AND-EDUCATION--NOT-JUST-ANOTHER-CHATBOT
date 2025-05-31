from pymongo import MongoClient
import json
import datetime
from datetime import timedelta, datetime
from collections import Counter
import os
from dotenv import load_dotenv
from pymongo.server_api import ServerApi
import src.CustomizedCalendar


#print(len([x for x in db['conversations'].find()]))


#Pulls gpt conversations from mongodb and formats them question answers in json format.
def getConversations():
    collection = db['conversations']  # replace 'collection_name' with your collection's name
    jsonString = '{"chats":['

    for document in collection.find():
        #print(document)
        #jsonString += '"query",{"data":[' #TODO fix wrong json format???
        if len(document['messages']) == 1: #Edgecase if message exists but no message from user sendt
            continue
        jsonString += '{"data":['
        for x in range(1, len(document['messages'])):
            if document['messages'][x]['from'] == 'user':
                jsonString += '{'

                jsonString += '"question":' + '"' + str(document['messages'][x]['content']).replace('"', "'") + '"'
                # jsonString += '"time":' + '"' + str(document['messages'][x]['createdAt']).replace('"', "'") + '"'

                jsonString += '},'


        jsonString = jsonString[:-1]

        jsonString += ']},'
    jsonString = jsonString[:-1]


    return " ".join((jsonString + "]}").splitlines())

#print(getConversations())

def dbToJson():
    collection = db['conversations']  # replace 'collection_name' with your collection's name
    jsonString = '{"chats":['

    for document in collection.find():
        for x in range(1, len(document['messages']), 2):
            jsonString += '{'

            jsonString += '"question":' + '"' + str(document['messages'][x]['content']).replace('"', "'") + '"' + ','
            #jsonString += '"answer":' + '"' + str(document['messages'][x + 1]['content']).replace('"', "'") + '"' + ','
            jsonString += '"time":' + '"' + str(document['messages'][x]['createdAt']).replace('"', "'") + '"'

            jsonString += '},'
    jsonString = jsonString[:-1] #Removes the last ,

    return " ".join((jsonString + "]}").splitlines())

#print(dbToJson())

def getNumberOfUsers(db):
    collection = db['users']
    return len(list(collection.find()))

def getNumberOfNewUsersThisWeek(db, start_date, end_date):
    collection = db['users']
    return len(list(collection.find({'createdAt': {'$gte': start_date, '$lte': end_date}})))

def getNumberOfMessagesThisWeek(db, start_date, end_date):
    collection = db['conversations']
    counter = 0
    for conversation in collection.find({'updatedAt': {'$gte': start_date, '$lte': end_date}}):
        for message in conversation['messages']:
            if message['createdAt'] > start_date and message['from'] == 'user':
                counter += 1
    return counter

def activeUsersThisWeek(db, start_date, end_date, calendar):
    collection = db['conversations']

    users = []
    for document in collection.find({'updatedAt': {'$gte': start_date, '$lte': end_date}}):
        date = str(document['updatedAt'])
        if "." not in date:
            date += ".000000"
        users.append((calendar.calculate(datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f"))[1]))
    weekDict = {i: [] for i in set(users)}

    for document in collection.find({'updatedAt': {'$gte': start_date, '$lte': end_date}}):
        for message in document['messages']:
            date = str(message['updatedAt'])
            if "." not in date:
                date += ".000000"
            #if my_calendar.calculate(datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f"))[1]:
                #print(message['userId'])
            weekDict[calendar.calculate(datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f"))[1]].append(document['userId'])
    #print([(x, len(set(weekDict.get(x)))) for x in weekDict])
    return [(x, len(set(weekDict.get(x)))) for x in weekDict]

def getDayHeatMapThisWeek(start_date, end_date):
    collection = db['conversations']
    hourDict = {i: 0 for i in range(24)}

    for document in collection.find({'updatedAt': {'$gte': start_date, '$lte': end_date}}):
        for messages in document['messages']:
            if messages['createdAt'] > start_date and messages['from'] == 'user':
                date = str(messages['updatedAt'])
                if "." not in date:
                    date += ".000000"
                hourDict[datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f").time().hour] += 1
    hourList = [(k, hourDict.get(k)) for k in hourDict.keys()]
    return hourList

def getWeekHeatMapThisWeek(start_date, end_date):
    collection = db['conversations']

    dayDict = {i: 0 for i in range(7)}
    for document in collection.find({'updatedAt': {'$gte': start_date, '$lte': end_date}}):
        for messages in document['messages']:
            if messages['createdAt'] > start_date and messages['from'] == 'user':
                date = str(messages['updatedAt'])
                if "." not in date:
                    date += ".000000"
                dayDict[datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f").weekday()] += 1
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return [(days_of_week[(k+0)%7], dayDict.get((k+0)%7), str(0) + str(k) + "-" + days_of_week[(k+0)%7]) for k in dayDict.keys()]


def getNumberOfConversationsThisWeek(start_date, end_date):
    collection = db['conversations']
    return len(list(collection.find({'createdAt': {'$gte': start_date, '$lte': end_date}})))

def getConversationsThisWeek(db ,start_date, end_date):
    collection = db['conversations']
    conversations = []

    for conversation in collection.find({'updatedAt': {'$gte': start_date, '$lte': end_date}}):
        conversations.append(conversation)
    return conversations



def numberOfConversationsPerUser():
    collection = db['conversations']
    userCount = [0] * getNumberOfUsers()
    userId = []

    for document in collection.find():
        userIdString = str(document['userId'])
        if userIdString not in userId:
            userId.append(userIdString)


        if userIdString in userId:
            userCount[userId.index(userIdString)] += 1
    return userCount

def numberOfMessagesPerUser():
    collection = db['conversations']
    userCount = [0] * getNumberOfUsers()
    userId = []

    for document in collection.find():
        userIdString = str(document['userId'])
        if userIdString not in userId:
            userId.append(userIdString)

        if userIdString in userId:
            counter = 0
            for messages in document['messages']:
                if messages['from'] == 'user':
                    counter += 1

            userCount[userId.index(userIdString)] += counter
    return userCount

#frequencyList list of int, number of messages each day
#datelist list of datetime.date(year-month-day)
def numberOfMessagesPerDay():
    collection = db['conversations']
    oneday = timedelta(days=1)

    firstDay = 0
    for document in collection.find():
        firstDay = document['createdAt'].date()
        break

    today = datetime.datetime.now().date()

    frequencyList = [0] * ((today - firstDay).days + 1)
    datelist = [firstDay+oneday*x for x in range(len(frequencyList))]

    for document in collection.find():
        for message in document['messages']:
            if message["from"] == "user":
                frequencyList[(firstDay-message['createdAt'].date()).days] += 1

    return frequencyList,datelist

def getMessagesAskedToday():
    collection = db['conversations']
    today = datetime.datetime.now().date()
    messaagesAskedToday = []

    for document in collection.find():
        for message in document['messages']:
            if message["createdAt"].date() == today:
                messaagesAskedToday.append(message)

    return messaagesAskedToday



def extractQuestion(conversation):
    questions = []

    convo = json.loads(conversation)
    for chats in convo['chats']:
        for data in chats['data']:
            questions.append(data['question'])
    return questions
