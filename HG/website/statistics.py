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
from users import *
import json

@csrf_exempt
@checkauth
def repayplan(req):
    if not checkjurisdiction(req,"还款计划"):
        a = {'user':req.user}
        return render_to_response("jur.html",a)
    
    if req.method == "GET":
        fromdate = req.GET.get("fromdate",str(datetime.date.today()))
        todate = req.GET.get("todate",str(datetime.date.today()+datetime.timedelta(7))) #未来一周
        if fromdate=="": fromdate = "1976-10-11"
        if todate=="": todate="2050-10-11"
        items = repayitem.objects.filter(repaydate__gte=fromdate,repaydate__lte=todate,status__gt=-1)
        daymap = {}
        for item in items:
            if item.repaydate in daymap:
                daymap[item.repaydate].append(item)
            else:
                daymap[item.repaydate] = [item]
        dayinfo = {}
        totalrepay = [0,0,0,0,0,0]
        # 返息笔数 返息金额 已返笔数 已返金额 待返笔数 待返金额 
        for item in daymap:
            for elem in daymap[item]:
                cnt = float(elem.repaymoney)
                
                if not item in dayinfo:
                    dayinfo[item] = [0,0,0,0,0,0]
                dayinfo[item][0] += 1
                totalrepay[0] += 1
                dayinfo[item][1] += cnt
                totalrepay[1] += cnt
                if elem.status==1:
                    dayinfo[item][4] += 1
                    totalrepay[4] += 1
                    dayinfo[item][5] += cnt
                    totalrepay[5] += cnt
                else:
                    dayinfo[item][2] += 1
                    totalrepay[2] += 1
                    dayinfo[item][3] += cnt
                    totalrepay[3] += cnt
        sortedlist = sorted(dayinfo.items(), key=lambda d: d[0], reverse=False)
        a = {"user":req.user}
        a["days"] = sortedlist
        a["totalrepay"] = totalrepay
        a["fromdate"] = fromdate
        a["todate"] = todate
        return render_to_response("repayplan.html",a)

@checkauth
def dayrepay(req,onedate):
    a = {'user':req.user}
    if not checkjurisdiction(req,"还款计划"):
        return render_to_response("jur.html",a)
    
    if req.method == "POST":
        return
    items = repayitem.objects.filter(repaydate__exact=onedate,status__gt=-1)
    totalrepay = [0,0,0,0,0,0]
    for elem in items:
        cnt = float(elem.repaymoney)
        if elem.status==3:
            cnt -= float(elem.thiscontract.money)
        totalrepay[0] += 1
        totalrepay[1] += cnt
        if elem.status==1:
            totalrepay[4] += 1
            totalrepay[5] += cnt
        else:
            totalrepay[2] += 1
            totalrepay[3] += cnt
    a = {"user":req.user}
    a["items"] = items
    a["day"] = onedate
    a["totalrepay"] = totalrepay
    return render_to_response("dayrepay.html",a)

def getitems(req):
    fromdate = req.GET.get("fromdate",str(datetime.date.today()-datetime.timedelta(7)))
    todate = req.GET.get("todate",str(datetime.date.today()))
        
    field_id = int(req.GET.get("field_id","-1"))
    party_id = int(req.GET.get("party_id","-1"))
    bigparty_id = int(req.GET.get("bigparty_id","-1"))
    manager_id = int(req.GET.get("manager_id","-1"))
    items = []
    if manager_id != -1:
        items = contract.objects.filter(startdate__gte=fromdate,startdate__lte=todate,thismanager_id=manager_id,status__gt=-1)
    elif party_id != -1:
        ms = manager.objects.filter(thisparty_id=party_id)
        for m in ms:
            items.extend(contract.objects.filter(startdate__gte=fromdate,
                startdate__lte=todate,thismanager_id=m.id,status__gt=-1))
    elif bigparty_id != -1:
        ps = party.objects.filter(thisbigparty_id=bigparty_id)
        for p in ps:
            ms = manager.objects.filter(thisparty_id=p.id)
            for m in ms:
                items.extend(contract.objects.filter(startdate__gte=fromdate,
                    startdate__lte=todate,thismanager_id=m.id,status__gt=-1))
    elif field_id != -1:
        bps = bigparty.objects.filter(thisfield_id=field_id)
        for bp in bps:
            ps = party.objects.filter(thisbigparty_id=bp.id)
            for p in ps:
                ms = manager.objects.filter(thisparty_id=p.id)
                for m in ms:
                    items.extend(contract.objects.filter(startdate__gte=fromdate,
                        startdate__lte=todate,thismanager_id=m.id,status__gt=-1))
    else:
        items = contract.objects.filter(startdate__gte=fromdate,startdate__lte=todate,status__gt=-1)
        
    return items

@checkauth
def intocnt(req,a={},type_id=0):
    if not checkjurisdiction(req,"进账统计"):
        a = {'user':req.user}
        return render_to_response("jur.html",a)
    if req.method == "GET":
        
        items = getitems(req)
        totalmoney = 0.0
        for item in items:
            totalmoney += float(item.money)
        #a = {"user":req.user}
        a["totalmoney"] = "%.02f" % totalmoney
        a["cnt"] = len(items)
        fromdate = req.GET.get("fromdate",str(datetime.date.today()-datetime.timedelta(7)))
        todate = req.GET.get("todate",str(datetime.date.today()))
        a["fromdate"] = fromdate
        a["todate"] = todate
        if type_id==0:
            a["user"] = req.user
            a["fields"] = field.objects.all()
            return render_to_response("intocnt.html",a)
        jsonstr = json.dumps(a,ensure_ascii=False)
        return HttpResponse(jsonstr,content_type='application/javascript')
   
@checkauth
def getbigparties(req,which_type):
    if req.method == "GET":
        field_id = req.GET.get("field_id","")
        bps = bigparty.objects.filter(thisfield_id=int(field_id))
        a = {"message":"true"}
        plist = []
        for bp in bps:
            plist.append((bp.id,bp.name))
        a["bigparties"] = plist
        if which_type=="yearintocnt":
            return yearintocnt(req,a,1)
        elif which_type=="intocnt":
            return intocnt(req,a,1)
        elif which_type=="repaycnt":
            return repaycnt(req,a,1)
        elif which_type=="waitrepay":
            return waitrepay(req,a,1)

@checkauth
def getparties(req,which_type):
    if req.method == "GET":
        bigparty_id = req.GET.get("bigparty_id","")
        ps = party.objects.filter(thisbigparty_id=int(bigparty_id))
        a = {"message":"true"}
        plist = []
        for p in ps:
            plist.append((p.id,p.name))
        a["parties"] = plist
        if which_type=="yearintocnt":
            return yearintocnt(req,a,1)
        elif which_type=="intocnt":
            return intocnt(req,a,1)
        elif which_type=="repaycnt":
            return repaycnt(req,a,1)
        elif which_type=="waitrepay":
            return waitrepay(req,a,1)

@checkauth
def getmanagers(req,which_type):
    if req.method == "GET":
        party_id = req.GET.get("party_id","")
        ms = manager.objects.filter(thisparty_id=int(party_id))
        a = {"message":"true"}
        mlist = []
        for m in ms:
            mlist.append((m.id,m.name))
        a["managers"] = mlist
        if which_type=="yearintocnt":
            return yearintocnt(req,a,1)
        elif which_type=="intocnt":
            return intocnt(req,a,1)
        elif which_type=="repaycnt":
            return repaycnt(req,a,1)
        elif which_type=="waitrepay":
            return waitrepay(req,a,1)

@checkauth
def getpersoncnt(req,which_type):
    if req.method == "GET":
        a = {"message":"true"}
        if which_type=="yearintocnt":
            return yearintocnt(req,a,1)
        elif which_type=="intocnt":
            return intocnt(req,a,1)
        elif which_type=="repaycnt":
            return repaycnt(req,a,1)
        elif which_type=="waitrepay":
            return waitrepay(req,a,1)
    


@checkauth
def yearintocnt(req,a={},type_id=0):
    if not checkjurisdiction(req,"年化进账统计"):
        a = {'user':req.user}
        return render_to_response("jur.html",a)
    if req.method == "GET":
        items = getitems(req)
        totalmoney = 0.0
        for item in items:
            if item.thisproduct.closedtype == 'm':
                totalmoney += 12*float(item.money)/item.thisproduct.closedperiod
            elif item.thisproduct.closedtype == 'd':
                totalmoney += 365*float(item.money)/item.thisproduct.closedperiod
        #a = {"user":req.user}
        fromdate = req.GET.get("fromdate",str(datetime.date.today()-datetime.timedelta(7)))
        todate = req.GET.get("todate",str(datetime.date.today()))
        a["totalmoney"] = "%.02f" % totalmoney
        a["cnt"] = len(items)
        a["fromdate"] = fromdate
        a["todate"] = todate
        if type_id==0:
            a["user"] = req.user
            a["fields"] = field.objects.all()
            return render_to_response("yearintocnt.html",a)
        jsonstr = json.dumps(a,ensure_ascii=False)
        return HttpResponse(jsonstr,content_type='application/javascript')

@checkauth
def repaycnt(req,a={},type_id=0):
    if not checkjurisdiction(req,"返款统计"):
        a = {'user':req.user}
        return render_to_response("jur.html",a)
    
    if req.method == "GET":
        fromdate = req.GET.get("fromdate",str(datetime.date.today()-datetime.timedelta(7)))
        todate = req.GET.get("todate",str(datetime.date.today()))
        #if fromdate=="": fromdate = "1976-10-11"
        #if todate=="": todate="2050-10-11"
        field_id = int(req.GET.get("field_id","-1"))
        bigparty_id = int(req.GET.get("bigparty_id","-1"))
        party_id = int(req.GET.get("party_id","-1"))
        manager_id = int(req.GET.get("manager_id","-1"))
        
        anslist = []
        items = repayitem.objects.filter(repaydate__gte=fromdate,repaydate__lte=todate,status__gt=-1)
        if manager_id != -1:
            for item in items:    
                if item.thiscontract.thismanager.id == manager_id:
                    anslist.append(item)
        elif party_id != -1:
            for item in items:    
                if item.thiscontract.thismanager.thisparty.id == party_id:
                    anslist.append(item)
        elif bigparty_id != -1:
            for item in items:    
                if item.thiscontract.thismanager.thisparty.thisbigparty.id == bigparty_id:
                    anslist.append(item)
        elif field_id != -1:
            for item in items:    
                if item.thiscontract.thismanager.thisparty.thisbigparty.thisfield.id == field_id:
                    anslist.append(item)
        else:
            anslist = items
            
        totalmoney = 0.0
        for item in anslist:
            totalmoney += float(item.repaymoney)
        a["totalmoney"] = "%.02f" % totalmoney
        a["cnt"] = len(anslist)
        a["fromdate"] = fromdate
        a["todate"] = todate
        if type_id==0:
            a["user"] = req.user
            a["fields"] = field.objects.all()
            return render_to_response("repaycnt.html",a)
        jsonstr = json.dumps(a,ensure_ascii=False)
        return HttpResponse(jsonstr,content_type='application/javascript')

@checkauth
def waitrepay(req,a={},type_id=0):
    if not checkjurisdiction(req,"待收查询"):
        a = {'user':req.user}
        return render_to_response("jur.html",a)
    
    if req.method == "GET":
        field_id = int(req.GET.get("field_id","-1"))
        party_id = int(req.GET.get("party_id","-1"))
        bigparty_id = int(req.GET.get("bigparty_id","-1"))
        manager_id = int(req.GET.get("manager_id","-1"))
        anslist = []
        items = list(repayitem.objects.filter(status=1))
        items.extend(list(repayitem.objects.filter(status=3)))
        if manager_id != -1:
            for item in items:    
                if item.thiscontract.thismanager.id == manager_id:
                    anslist.append(item)
        elif party_id != -1:
            for item in items:    
                if item.thiscontract.thismanager.thisparty.id == party_id:
                    anslist.append(item)
        elif bigparty_id != -1:
            for item in items:    
                if item.thiscontract.thismanager.thisparty.thisbigparty.id == bigparty_id:
                    anslist.append(item)
        elif field_id != -1:
            for item in items:    
                if item.thiscontract.thismanager.thisparty.thisbigparty.thisfield.id == field_id:
                    anslist.append(item)
        else:
            anslist = items
            
        totalmoney = 0.0
        for item in anslist:
            totalmoney += float(item.repaymoney)
            
        a["totalmoney"] = "%.02f" % totalmoney
        a["cnt"] = len(anslist)
        if type_id==0:
            a["user"] = req.user
            a["fields"] = field.objects.all()
            return render_to_response("waitrepay.html",a)
        jsonstr = json.dumps(a,ensure_ascii=False)
        return HttpResponse(jsonstr,content_type='application/javascript')
