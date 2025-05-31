from pymongo import MongoClient, DESCENDING
from pymongo.server_api import ServerApi
import datetime
from dotenv import load_dotenv
import os
load_dotenv()

#client = MongoClient('localhost', 27016, username="username", password="password")
#db = client['chat-analysis']

uri = os.getenv("teachertooldb")
db = MongoClient(uri, server_api=ServerApi('1')).MSC01


#print(len([x for x in db['chat-analysis'].find()]))


def addItem(content: dict, collection: str):
    collections = db[collection]

    #Add dict type for content
    content.update({"LastUpdated": str(datetime.datetime.now())})
    collections.insert_one(content)
def addItemWithCollection(content: dict, collection):
    content.update({"LastUpdated": str(datetime.datetime.now())})
    collection.insert_one(content)
#Used for weeklyupdates, need to change the dict before function call
def updateItem(content: dict, collection):
    content.update({"LastUpdated": str(datetime.datetime.now())})
    if "_id" in content:
        content.pop("_id")
    collection.replace_one({}, content, upsert=True)

#Used for retriving analysed data from "Teacher analys tool"
def getLatest(collection: str):
    collections = db[collection]
    sort_criteria = [("LastUpdated", DESCENDING)]
    item = None
    try:
        if collections.count_documents() == 0:
            return None
        item = collections.find(sort=sort_criteria).next()

    finally:
        return item

def getMainWeeklyReportCollection():
    return db['weeklyReport']

def getWeeklyReport():
    return getMainWeeklyReportCollection().find_one()
def getWeeklyReportByNumber(weekNumber):
    return db['weeklyReport' + str(weekNumber)].find_one()

def createCollection(collectionName):
    return db.create_collection(collectionName)

def getAll(collection: str):
    collections = db[collection]

    items = []
    for collection in collections.find():
        items.append(collection)

    return items

def getPastWeeklyReportCollections(weekList):
    collectionList = []
    for weekNumber in weekList:
        collectionList.append(db["weeklyReport" + str(weekNumber)])

    return collectionList

def getPastWeeklyReports(listOfWeeklyReportCollections):
    collectionList = []
    for collection in listOfWeeklyReportCollections:
        collectionList.append(collection.find_one())

    return collectionList

def updateTrend(document, filter):
    collection = db["trends"]
    collection.replace_one(filter, document, upsert=True)

def getWeeklyChange():
    return db["weeklyChange"].find_one()

def getSummary():
    return db["summary"].find_one()

def updateSummary(content):
    collection = db["summary"]
    json = {'Summary': content,
            'LastUpdated': str(datetime.datetime.now())}
    return collection.replace_one({}, json, upsert=True)

def weeklyChange(content):
    collection = db["weeklyChange"]
    json = {'weeklyChange': content,
            'LastUpdated': str(datetime.datetime.now())}
    return collection.replace_one({}, json, upsert=True)

#print(weeklyChange("new summary"))