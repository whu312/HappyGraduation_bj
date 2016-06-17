from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render_to_response
import sys
import datetime
from website.models import *
from django.contrib import auth
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
import re
from django.views.decorators.csrf import csrf_exempt
from days import *

product_rate = 0.32

def AjustDate(thisdate):
    oneday = thisdate.day
    endday = ((oneday-1)/10+1)*10
    if endday==30:
        endday += 1
    while True:
        try:
            ansdate = datetime.date(thisdate.year,thisdate.month,endday)
            return ansdate
        except:
            endday -= 1
    
def CreateRepayItem(onecontract):
    thisproduct = onecontract.thisproduct
    repaycycle = thisproduct.repaycycle
    intmoney = float(onecontract.money)
    if repaycycle.cycletype == 1: #once
        thisdate = datetime.datetime.strptime(onecontract.enddate,'%Y-%m-%d').date()
        startdate = datetime.datetime.strptime(onecontract.startdate,'%Y-%m-%d').date()
        totalmoney = 0.0
        if thisproduct.closedtype == 'm':
            totalmoney = intmoney + intmoney*float(thisproduct.rate)/1200*thisproduct.closedperiod
            #leftdays = getDays(getNextDay(startdate,thisproduct.closedperiod,0),thisdate)
            #totalmoney += intmoney*float(thisproduct.rate)/36500*leftdays
        elif thisproduct.closedtype == 'd':
            totalmoney = intmoney + intmoney*float(thisproduct.rate)/36500*thisproduct.closedperiod
            #leftdays = getDays(getNextDay(startdate,0,thisproduct.closedperiod),thisdate)
            #totalmoney += intmoney*float(thisproduct.rate)/36500*leftdays
        repaydate = thisdate
        thisrepayitem = repayitem(repaydate=str(repaydate),repaymoney=str(int(totalmoney+0.5)),repaytype=3,
                status=1,thiscontract=onecontract)
        thisrepayitem.save()
        #
        totalmoney -= intmoney
        totalmoney = totalmoney/product_rate * (1-product_rate)
        thisrepayitem = repayitem(repaydate=str(repaydate),repaymoney=str(int(totalmoney+0.5)),repaytype=3,
                status=11,thiscontract=onecontract)
        thisrepayitem.save()
        #
        
        
    elif repaycycle.cycletype == 2: #every month
        thisdate = datetime.datetime.strptime(onecontract.enddate,'%Y-%m-%d').date()
        startdate = datetime.datetime.strptime(onecontract.startdate,'%Y-%m-%d').date()
        monthmoney = intmoney*float(thisproduct.rate)/1200
        for i in range(0,thisproduct.closedperiod-1):        
            startdate = getNextDay(startdate,1,0)
            #print startdate
            repaydate = AjustDate(startdate)
            #print repaydate
            monthrepayitem = repayitem(repaydate=str(repaydate),repaymoney=str(int(monthmoney+0.5)),repaytype=1,
                status=1,thiscontract=onecontract)
            monthrepayitem.save()
            
            tmpmonthrepayitem = repayitem(repaydate=str(repaydate),repaymoney=str(int(monthmoney/product_rate*(1-product_rate)+0.5)),
                repaytype=1,status=11,thiscontract=onecontract)
            tmpmonthrepayitem.save()
        
        repaydate = thisdate
        monthrepayitem = repayitem(repaydate=str(repaydate),repaymoney=str(int(monthmoney+intmoney+0.5)),repaytype=2,
            status=1,thiscontract=onecontract)
        monthrepayitem.save()
        tmpmonthrepayitem = repayitem(repaydate=str(repaydate),repaymoney=str(int(monthmoney/product_rate*(1-product_rate)+0.5)),
            repaytype=2,status=11,thiscontract=onecontract)
        tmpmonthrepayitem.save()
