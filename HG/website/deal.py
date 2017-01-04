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
            totalmoney = intmoney*float(thisproduct.rate)/1200*thisproduct.closedperiod
            #leftdays = getDays(getNextDay(startdate,thisproduct.closedperiod,0),thisdate)
            #totalmoney += intmoney*float(thisproduct.rate)/36500*leftdays
        elif thisproduct.closedtype == 'd':
            totalmoney = intmoney*float(thisproduct.rate)/36500*thisproduct.closedperiod
            #leftdays = getDays(getNextDay(startdate,0,thisproduct.closedperiod),thisdate)
            #totalmoney += intmoney*float(thisproduct.rate)/36500*leftdays
        repaydate = thisdate
        thisrepayitem = repayitem(repaydate=str(repaydate),repaymoney=str(int(totalmoney+0.5)),repaytype=1,
                status=1,thiscontract=onecontract)
        thisrepayitem.save()
        thisrepayitem = repayitem(repaydate=str(repaydate),repaymoney=str(int(intmoney+0.5)),repaytype=3,
                status=1,thiscontract=onecontract)
        thisrepayitem.save()
        #
        totalmoney = totalmoney/product_rate * (1-product_rate)
        thisrepayitem = repayitem(repaydate=str(repaydate),repaymoney=str(int(totalmoney+0.5)),repaytype=1,
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
        monthrepayitem = repayitem(repaydate=str(repaydate),repaymoney=str(int(monthmoney+0.5)),repaytype=1,
            status=1,thiscontract=onecontract)
        monthrepayitem.save()
        
        monthrepayitem = repayitem(repaydate=str(repaydate),repaymoney=str(int(intmoney+0.5)),repaytype=2,
            status=1,thiscontract=onecontract)
        monthrepayitem.save()
        
        tmpmonthrepayitem = repayitem(repaydate=str(repaydate),repaymoney=str(int(monthmoney/product_rate*(1-product_rate)+0.5)),
            repaytype=1,status=11,thiscontract=onecontract)
        tmpmonthrepayitem.save()

def IsRepayItemRepeated(oneitem):
    repays = repayitem.objects.filter(repaydate=oneitem.repaydate, repaymoney=oneitem.repaymoney, repaytype=oneitem.repaytype,
        thiscontract_id=oneitem.thiscontract.id)
    for item in repays:
        if abs(item.status - oneitem.status) < 5:
            return True
    return False
    
def AjustProduct4Contract(onecontract, oneproduct):
    thisproduct = oneproduct
    repaycycle = thisproduct.repaycycle
    intmoney = float(onecontract.money)
    if repaycycle.cycletype == 1: #once
        thisdate = datetime.datetime.strptime(onecontract.enddate,'%Y-%m-%d').date()
        startdate = datetime.datetime.strptime(onecontract.startdate,'%Y-%m-%d').date()
        firststartdate = datetime.datetime.strptime(onecontract.startdate,'%Y-%m-%d').date()
        totalmoney = 0.0
        if thisproduct.closedtype == 'm':
            totalmoney = intmoney*float(thisproduct.rate)/1200*thisproduct.closedperiod
            firststartdate = getNextDay(startdate, thisproduct.closedtype, 0)
            #leftdays = getDays(getNextDay(startdate,thisproduct.closedperiod,0),thisdate)
            #totalmoney += intmoney*float(thisproduct.rate)/36500*leftdays
        elif thisproduct.closedtype == 'd':
            totalmoney = intmoney*float(thisproduct.rate)/36500*thisproduct.closedperiod
            firststartdate = getNextDay(startdate, 0, thisproduct.closedtype)
            #leftdays = getDays(getNextDay(startdate,0,thisproduct.closedperiod),thisdate)
            #totalmoney += intmoney*float(thisproduct.rate)/36500*leftdays
        repaydate = firststartdate
        thisrepayitem = repayitem(repaydate=str(repaydate),repaymoney=str(int(totalmoney+0.5)),repaytype=1,
                status=1,thiscontract=onecontract)
        
        if not IsRepayItemRepeated(thisrepayitem):
            thisrepayitem.save()
            
        thisrepayitem = repayitem(repaydate=str(repaydate),repaymoney=str(int(intmoney+0.5)),repaytype=3,
                status=1,thiscontract=onecontract)
        thisrepayitem.save()
        
        delrepayitems = repayitem.objects.filter(thiscontract_id=onecontract.id, repaytype=3)
        for delitem in delrepayitems:
            delitem.delete()
    
        #
        totalmoney = totalmoney/product_rate * (1-product_rate)
        thisrepayitem = repayitem(repaydate=str(repaydate),repaymoney=str(int(totalmoney+0.5)),repaytype=1,
                status=11,thiscontract=onecontract)
        
        if not IsRepayItemRepeated(thisrepayitem):
            thisrepayitem.save()
        return repaydate
        #
        
    elif repaycycle.cycletype == 2: #every month
        thisdate = datetime.datetime.strptime(onecontract.enddate,'%Y-%m-%d').date()
        startdate = datetime.datetime.strptime(onecontract.startdate,'%Y-%m-%d').date()
        firststartdate = datetime.datetime.strptime(onecontract.startdate,'%Y-%m-%d').date()
        monthmoney = intmoney*float(thisproduct.rate)/1200
        
        delrepayitems = repayitem.objects.filter(thiscontract_id=onecontract.id, repaytype=2)
        for delitem in delrepayitems:
            delitem.delete()
        
        delrepayitems = repayitem.objects.filter(thiscontract_id=onecontract.id, repaydate=str(thisdate), repaytype=1)
        for delitem in delrepayitems:
            delitem.delete()
            
        for i in range(0,thisproduct.closedperiod-1):        
            startdate = getNextDay(startdate,1,0)
            #print startdate
            repaydate = AjustDate(startdate)
            monthrepayitem = repayitem(repaydate=str(repaydate),repaymoney=str(int(monthmoney+0.5)),repaytype=1,
                status=1,thiscontract=onecontract)
            if not IsRepayItemRepeated(monthrepayitem):
                print "not repeated"
                monthrepayitem.save()
            
            tmpmonthrepayitem = repayitem(repaydate=str(repaydate),repaymoney=str(int(monthmoney/product_rate*(1-product_rate)+0.5)),
                repaytype=1,status=11,thiscontract=onecontract)
            if not IsRepayItemRepeated(tmpmonthrepayitem):
                tmpmonthrepayitem.save()
        
        repaydate = getNextDay(firststartdate, thisproduct.closedperiod, 0)
        monthrepayitem = repayitem(repaydate=str(repaydate),repaymoney=str(int(monthmoney+0.5)),repaytype=1,
            status=1,thiscontract=onecontract)
        if not IsRepayItemRepeated(monthrepayitem):
            monthrepayitem.save()
            
        monthrepayitem = repayitem(repaydate=str(repaydate),repaymoney=str(int(intmoney+0.5)),repaytype=2,
            status=1,thiscontract=onecontract)
        monthrepayitem.save()
        
        
        tmpmonthrepayitem = repayitem(repaydate=str(repaydate),repaymoney=str(int(monthmoney/product_rate*(1-product_rate)+0.5)),
            repaytype=1,status=11,thiscontract=onecontract)
        if not IsRepayItemRepeated(tmpmonthrepayitem):
            tmpmonthrepayitem.save()
        return repaydate
