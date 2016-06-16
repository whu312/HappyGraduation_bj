import sys
import datetime
def getNextDay(onedate,months,days):
    thisdate = onedate
    if thisdate.month+months>12:
        try:
            heremonth = (thisdate.month+months)%12
            if heremonth == 0:
                heremonth = 12
            thisdate = datetime.date(thisdate.year+1,heremonth,thisdate.day)
        except:
            nowday = thisdate.day
            while True:
                try:
                    thisdate = datetime.date(thisdate.year+1,(thisdate.month+months)%12,nowday-1)
                    break
                except:
                    nowday -= 1
                    continue 
    else:
        try:
            thisdate = datetime.date(thisdate.year,thisdate.month+months,thisdate.day)
        except:
            nowday = thisdate.day
            while True:
                try:
                    thisdate = datetime.date(thisdate.year,thisdate.month+months,nowday-1)
                    break
                except:
                    nowday -= 1
                    continue               
    thisdate -= datetime.timedelta(days)
    return thisdate
def getPreDay(onedate,months,days): # months<=12
    thisdate = onedate
    if thisdate.month-months<1:
        try:
            heremonth = (thisdate.month+12-months)
            thisdate = datetime.date(thisdate.year-1,heremonth,thisdate.day)
        except:
            nowday = thisdate.day
            while True:
                try:
                    thisdate = datetime.date(thisdate.year-1,heremonth,nowday-1)
                    break
                except:
                    nowday -= 1
                    continue 
    else:
        try:
            thisdate = datetime.date(thisdate.year,thisdate.month-months,thisdate.day)
        except:
            nowday = thisdate.day
            while True:
                try:
                    thisdate = datetime.date(thisdate.year,thisdate.month-months,nowday-1)
                    break
                except:
                    nowday -= 1
                    continue               
    thisdate += datetime.timedelta(days)
    return thisdate

def getDays(startday,endday):
    cnt = 0
    thisstart = startday
    thisend = endday
    while thisstart < thisend:
        thisstart += datetime.timedelta(1)
        cnt += 1
    return cnt
