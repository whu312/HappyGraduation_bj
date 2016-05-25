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

copy_rate= 0.32

def CreateRepayItem(onecontract):
    thisproduct = onecontract.thisproduct
    repaycycle = thisproduct.repaycycle
    intmoney = float(onecontract.money)
    if repaycycle.cycletype == 1: #once
        if thisproduct.closedtype == 'm':
            totalmoney = intmoney + intmoney*float(thisproduct.rate)/1200*thisproduct.closedperiod
        elif thisproduct.closedtype == 'd':
            totalmoney = intmoney + intmoney*float(thisproduct.rate)/36500*thisproduct.closedperiod
        thisrepayitem = repayitem(repaydate=onecontract.enddate,repaymoney=str(int((totalmoney-intmoney)*copy_rate+intmoney+0.5)),repaytype=3,
                status=1,thiscontract=onecontract)
        thisrepayitem.save()
        
        #copy
        thisrepayitem2 = repayitem(repaydate=onecontract.enddate,repaymoney=str(int((totalmoney-intmoney)*(1-copy_rate)+intmoney+0.5)),repaytype=1,
                status=1,thiscontract=onecontract)
        thisrepayitem2.save()
        #
        
    elif repaycycle.cycletype == 2: #every month
        thisdate = datetime.datetime.strptime(onecontract.enddate,'%Y-%m-%d').date()
        startdate = datetime.datetime.strptime(onecontract.startdate,'%Y-%m-%d').date()
        tmpdate1 = getNextDay(startdate,1,0)
        tmpdate2 = getNextDay(tmpdate1,1,0)
        if thisdate>=tmpdate2:
            firstmoney = intmoney + intmoney*float(thisproduct.rate)/1200
            lastrepayitem = repayitem(repaydate=onecontract.enddate,repaymoney=str(int((firstmoney-intmoney)*copy_rate+intmoney+0.5)),repaytype=2,
                    status=1,thiscontract=onecontract)
            lastrepayitem.save()
            #copy
            lastrepayitem2 = repayitem(repaydate=onecontract.enddate,repaymoney=str(int((firstmoney-intmoney)*(1-copy_rate)+intmoney+0.5)),repaytype=1,
                    status=1,thiscontract=onecontract)
            lastrepayitem2.save()
            #
            thisdate = getPreDay(thisdate,1,0)
        monthmoney = intmoney*float(thisproduct.rate)/1200
        while thisdate>=tmpdate2:
            monthrepayitem = repayitem(repaydate=str(thisdate),repaymoney=str(int(monthmoney*copy_rate+0.5)),repaytype=1,
                status=1,thiscontract=onecontract)
            monthrepayitem.save()
            #copy
            monthrepayitem2 = repayitem(repaydate=str(thisdate),repaymoney=str(int(monthmoney*(1-copy_rate)+0.5)),repaytype=1,
                status=1,thiscontract=onecontract)
            monthrepayitem2.save()
            #
            thisdate = getPreDay(thisdate,1,0)
        if tmpdate1<=thisdate:
            tmpdate3 = getPreDay(thisdate,1,0)
            days = getDays(startdate,tmpdate3)
            lastmoney = monthmoney + intmoney*float(thisproduct.rate)/36500*days
            monthrepayitem = repayitem(repaydate=str(thisdate),repaymoney=str(int((lastmoney-monthmoney)*copy_rate+monthmoney+0.5)),repaytype=1,
                status=1,thiscontract=onecontract)
            monthrepayitem.save()
            #copy
            monthrepayitem2 = repayitem(repaydate=str(thisdate),repaymoney=str(int((lastmoney-monthmoney)*(1-copy_rate)+monthmoney+0.5)),repaytype=1,
                status=1,thiscontract=onecontract)
            monthrepayitem2.save()
            #
        else:
            days = getDays(startdate,thisdate)
            lastmoney = intmoney + intmoney*float(thisproduct.rate)/36500*days
            monthrepayitem = repayitem(repaydate=str(thisdate),repaymoney=str(int((lastmoney-intmoney)*copy_rate+intmoney+0.5)),repaytype=2,
                status=1,thiscontract=onecontract)
            monthrepayitem.save()
            #copy
            monthrepayitem2 = repayitem(repaydate=str(thisdate),repaymoney=str(int((lastmoney-intmoney)*(1-copy_rate)+intmoney+0.5)),repaytype=1,
                status=1,thiscontract=onecontract)
            monthrepayitem2.save()
            #
