from src import CustomizedCalendar
from datetime import datetime, timedelta

WEEK = CustomizedCalendar.WEEKDAY
calender = CustomizedCalendar.CustomizedCalendar(start_weekday=WEEK.MON, indicator_weekday=WEEK.SAT)

def getDateFromLastWeek(timestamp):
    return timestamp - timedelta(days=7)

def getLastWeekWeekNumber(timestamp):
    return calender.calculate(getDateFromLastWeek(timestamp))[1]

def getTimeNow(): #api call without timestamp parameter
    return datetime.now()
