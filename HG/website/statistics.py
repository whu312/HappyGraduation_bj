﻿from django.shortcuts import render
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
from django.http import StreamingHttpResponse
from pyExcelerator import *

@csrf_exempt
@checkauth
def repayplan(req):
    a = {"user":req.user}
    a["indexlist"] = getindexlist(req)
    if not checkjurisdiction(req,"还款计划"):
        return render_to_response("jur.html",a)
    
    if req.method == "GET":
        fromdate = req.GET.get("fromdate",str(datetime.date.today()))
        todate = req.GET.get("todate",str(datetime.date.today()+datetime.timedelta(7))) #未来一周
        if fromdate=="": fromdate = "1976-10-11"
        if todate=="": todate="2050-10-11"
        items = repayitem.objects.filter(repaydate__gte=fromdate,repaydate__lte=todate,status__gt=0)
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
                if elem.status<10:
                    if not item in dayinfo:
                        dayinfo[item] = [0,0,0,0,0,0]
                    dayinfo[item][0] += 1
                    dayinfo[item][1] += cnt
                    if elem.status==1 or elem.status==3:
                        dayinfo[item][4] += 1
                        totalrepay[4] += 1
                        dayinfo[item][5] += cnt
                        totalrepay[5] += cnt
                    elif elem.status==2 or elem.status==4 :
                        dayinfo[item][2] += 1
                        totalrepay[2] += 1
                        dayinfo[item][3] += cnt
                        totalrepay[3] += cnt
                totalrepay[0] += 1
                totalrepay[1] += cnt
                if elem.status==11 or elem.status==13:
                    totalrepay[4] += 1
                    totalrepay[5] += cnt
                elif elem.status==12 or elem.status==14:
                    totalrepay[2] += 1
                    totalrepay[3] += cnt
        sortedlist = sorted(dayinfo.items(), key=lambda d: d[0], reverse=False)
        a["days"] = sortedlist
        a["totalrepay"] = totalrepay
        a["fromdate"] = fromdate
        a["todate"] = todate
        return render_to_response("repayplan.html",a)

@checkauth
def dayrepay(req,onedate):
    a = {'user':req.user}
    a["indexlist"] = getindexlist(req)
    if not checkjurisdiction(req,"还款计划"):
        return render_to_response("jur.html",a)
    
    if req.method == "POST":
        return
    items = repayitem.objects.filter(repaydate__exact=onedate,status__lt=10)
    totalrepay = [0,0,0,0,0,0]
    for elem in items:
        cnt = float(elem.repaymoney)
        #if elem.status==3:
        #    cnt -= float(elem.thiscontract.money)
        totalrepay[0] += 1
        totalrepay[1] += cnt
        if elem.status==1:
            totalrepay[4] += 1
            totalrepay[5] += cnt
        else:
            totalrepay[2] += 1
            totalrepay[3] += cnt
    a["items"] = items
    a["day"] = onedate
    a["totalrepay"] = totalrepay
    return render_to_response("dayrepay.html",a)

def getitems(req,lowest_status=0):
    fromdate = req.GET.get("fromdate",str(datetime.date.today()-datetime.timedelta(7)))
    todate = req.GET.get("todate",str(datetime.date.today()))
        
    field_id = int(req.GET.get("field_id","-1"))
    party_id = int(req.GET.get("party_id","-1"))
    bigparty_id = int(req.GET.get("bigparty_id","-1"))
    manager_id = int(req.GET.get("manager_id","-1"))
    items = []
    if manager_id != -1:
        items = contract.objects.filter(startdate__gte=fromdate,startdate__lte=todate,thismanager_id=manager_id,status__gte=lowest_status)
    elif party_id != -1:
        ms = manager.objects.filter(thisparty_id=party_id)
        for m in ms:
            items.extend(contract.objects.filter(startdate__gte=fromdate,
                startdate__lte=todate,thismanager_id=m.id,status__gte=lowest_status))
    elif bigparty_id != -1:
        ps = party.objects.filter(thisbigparty_id=bigparty_id)
        for p in ps:
            ms = manager.objects.filter(thisparty_id=p.id)
            for m in ms:
                items.extend(contract.objects.filter(startdate__gte=fromdate,
                    startdate__lte=todate,thismanager_id=m.id,status__gte=lowest_status))
    elif field_id != -1:
        bps = bigparty.objects.filter(thisfield_id=field_id)
        for bp in bps:
            ps = party.objects.filter(thisbigparty_id=bp.id)
            for p in ps:
                ms = manager.objects.filter(thisparty_id=p.id)
                for m in ms:
                    items.extend(contract.objects.filter(startdate__gte=fromdate,
                        startdate__lte=todate,thismanager_id=m.id,status__gte=lowest_status))
    else:
        items = contract.objects.filter(startdate__gte=fromdate,startdate__lte=todate,status__gte=lowest_status)
        
    return items

def GetEnddateItems(req):
    fromdate = req.GET.get("fromdate",str(datetime.date.today()-datetime.timedelta(7)))
    todate = req.GET.get("todate",str(datetime.date.today()))
        
    field_id = int(req.GET.get("field_id","-1"))
    party_id = int(req.GET.get("party_id","-1"))
    bigparty_id = int(req.GET.get("bigparty_id","-1"))
    manager_id = int(req.GET.get("manager_id","-1"))
    items = []
    if manager_id != -1:
        items = contract.objects.filter(enddate__gte=fromdate,enddate__lte=todate,thismanager_id=manager_id,status__gt=-1)
    elif party_id != -1:
        ms = manager.objects.filter(thisparty_id=party_id)
        for m in ms:
            items.extend(contract.objects.filter(enddate__gte=fromdate,
                enddate__lte=todate,thismanager_id=m.id,status__gt=-1))
    elif bigparty_id != -1:
        ps = party.objects.filter(thisbigparty_id=bigparty_id)
        for p in ps:
            ms = manager.objects.filter(thisparty_id=p.id)
            for m in ms:
                items.extend(contract.objects.filter(enddate__gte=fromdate,
                    enddate__lte=todate,thismanager_id=m.id,status__gt=-1))
    elif field_id != -1:
        bps = bigparty.objects.filter(thisfield_id=field_id)
        for bp in bps:
            ps = party.objects.filter(thisbigparty_id=bp.id)
            for p in ps:
                ms = manager.objects.filter(thisparty_id=p.id)
                for m in ms:
                    items.extend(contract.objects.filter(enddate__gte=fromdate,
                        enddate__lte=todate,thismanager_id=m.id,status__gt=-1))
    else:
        items = contract.objects.filter(enddate__gte=fromdate,enddate__lte=todate,status__gt=-1)
        
    return items

@checkauth
def intocnt(req,a={},type_id=0):
    if not checkjurisdiction(req,"进账统计"):
        a = {'user':req.user}
        a["indexlist"] = getindexlist(req)
        return render_to_response("jur.html",a)
    if req.method == "GET":
        items = getitems(req,4)
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
            a["indexlist"] = getindexlist(req)
            a["fields"] = field.objects.all()
            return render_to_response("intocnt.html",a)
        jsonstr = json.dumps(a,ensure_ascii=False)
        return HttpResponse(jsonstr,content_type='application/javascript')
   
@checkauth
def getbigparties(req,which_type='0'):
    if req.method == "GET":
        field_id = req.GET.get("field_id","")
        bps = bigparty.objects.filter(thisfield_id=int(field_id))
        a = {"message":"true"}
        plist = []
        for bp in bps:
            plist.append((bp.id,bp.name))
        a["bigparties"] = plist
        if which_type=='0':
            jsonstr = json.dumps(a,ensure_ascii=False)
            return HttpResponse(jsonstr,content_type='application/javascript')
        if which_type=="yearintocnt":
            return yearintocnt(req,a,1)
        elif which_type=="intocnt":
            return intocnt(req,a,1)
        elif which_type=="repaycnt":
            return repaycnt(req,a,1)
        elif which_type=="waitrepay":
            return waitrepay(req,a,1)

@checkauth
def getparties(req,which_type='0'):
    if req.method == "GET":
        bigparty_id = req.GET.get("bigparty_id","")
        ps = party.objects.filter(thisbigparty_id=int(bigparty_id))
        a = {"message":"true"}
        plist = []
        for p in ps:
            plist.append((p.id,p.name))
        a["parties"] = plist
        if which_type=='0':
            jsonstr = json.dumps(a,ensure_ascii=False)
            return HttpResponse(jsonstr,content_type='application/javascript')
        if which_type=="yearintocnt":
            return yearintocnt(req,a,1)
        elif which_type=="intocnt":
            return intocnt(req,a,1)
        elif which_type=="repaycnt":
            return repaycnt(req,a,1)
        elif which_type=="waitrepay":
            return waitrepay(req,a,1)

@checkauth
def getmanagers(req,which_type='0'):
    if req.method == "GET":
        party_id = req.GET.get("party_id","")
        ms = manager.objects.filter(thisparty_id=int(party_id))
        a = {"message":"true"}
        mlist = []
        for m in ms:
            mlist.append((m.id,m.name))
        a["managers"] = mlist
        if which_type=='0':
            jsonstr = json.dumps(a,ensure_ascii=False)
            return HttpResponse(jsonstr,content_type='application/javascript')
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
def renewalCnt(req):
    a = {'user':req.user}
    a["indexlist"] = getindexlist(req)
    if not checkjurisdiction(req,"续单统计"):
        return render_to_response("jur.html",a)
    if req.method == "GET":
        anslist = []
        items = GetEnddateItems(req)
        for item in items:
            if item.renewal_son_id!=-1:
                renewc = contract.objects.filter(id=item.renewal_son_id)[0]
                tmplist = [item,"是",renewc.money,renewc.thisproduct.name]
                anslist.append(tmplist)
            else:
                tmplist = [item,"否","",""]
                anslist.append(tmplist)
        
        anslist = sorted(anslist,key=lambda asd:asd[0].enddate)
        a["items"] = anslist
        
        fromdate = req.GET.get("fromdate",str(datetime.date.today()-datetime.timedelta(7)))
        todate = req.GET.get("todate",str(datetime.date.today()))
        a["fromdate"] = fromdate
        a["todate"] = todate
        a["fields"] = field.objects.all()
        fid = req.GET.get("field_id","-1")
        a["fid"] = int(fid)
        if fid!="-1":
            bps = bigparty.objects.filter(thisfield_id=int(fid))
            a["bigparty"] = True
            a["bigparties"] = bps
            bpid = req.GET.get("bigparty_id","-1")
            a["bpid"] = int(bpid)
            if bpid!="-1":
                ps = party.objects.filter(thisbigparty_id=int(bpid))
                a["party"] = True
                a["parties"] = ps
                pid = req.GET.get("party_id","-1")
                a["pid"] = int(pid)
                if pid!="-1":
                    ms = manager.objects.filter(thisparty_id=int(pid))
                    a["manager"] = True
                    a["managers"] = ms
                    mid = req.GET.get("manager_id","-1")
                    a["mid"] = int(mid)
                    
        return render_to_response("renewalCnt.html",a)

@checkauth
def outrenewalCnt(req):
    def file_iterator(file_name, chunk_size=512):
        with open(file_name,"rb") as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break
    def writefile(items):
        w = Workbook()
        ws = w.add_sheet('sheet1')
        titles = [u"合同号",u"客户名",u"产品",u"金额",u"到期日",u"客户经理",u"是否续签",u"续签金额",u"续签产品"]
        for i in range(0,len(titles)):
            ws.write(0,i,titles[i])
        for i in range(0,len(items)):
            ws.write(i+1,0,items[i][0].number)
            ws.write(i+1,1,items[i][0].client_name)
            ws.write(i+1,2,items[i][0].thisproduct.name)
            ws.write(i+1,3,items[i][0].money)
            ws.write(i+1,4,items[i][0].enddate)
            ws.write(i+1,5,items[i][0].thismanager.name)
            ws.write(i+1,6,items[i][1])
            ws.write(i+1,7,items[i][2])
            ws.write(i+1,8,items[i][3])
            
        filename = ".//tmpfolder//" + str(datetime.datetime.now()).split(" ")[1].replace(":","").replace(".","") + ".xls"
        w.save(filename)
        return filename
    if not checkjurisdiction(req,"经理统计"):
        return render_to_response("jur.html",a)
    if req.method == "GET":
        anslist = []
        items = GetEnddateItems(req)
        for item in items:
            if item.renewal_son_id!=-1:
                renewc = contract.objects.filter(id=item.renewal_son_id)[0]
                tmplist = [item,u"是",renewc.money,renewc.thisproduct.name]
                anslist.append(tmplist)
            else:
                tmplist = [item,u"否",u"",u""]
                anslist.append(tmplist)
        anslist = sorted(anslist,key=lambda asd:asd[0].enddate)
        
        the_file_name = writefile(anslist)
        response = StreamingHttpResponse(file_iterator(the_file_name))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{0}"'.format("年化进账统计.xls")
        return response


@checkauth
def managerYear(req):
    a = {'user':req.user}
    a["indexlist"] = getindexlist(req)
    if not checkjurisdiction(req,"经理统计"):
        return render_to_response("jur.html",a)
    if req.method == "GET":
        ansmap = {}
        items = getitems(req,4)
        for item in items:
            incnt = 0.0
            if item.thisproduct.closedtype == 'm':
                incnt += float(item.money)*item.thisproduct.closedperiod/12
            elif item.thisproduct.closedtype == 'd':
                incnt += float(item.money)*item.thisproduct.closedperiod/365
            if item.thismanager.id in ansmap:
                ansmap[item.thismanager.id][0] += incnt
            else:
                ansmap[item.thismanager.id] = [incnt,item.thismanager]
        
        tmplist = sorted(ansmap.iteritems(),key=lambda asd:asd[1][0],reverse=True)
        a["myearin"] = tmplist
        
        fromdate = req.GET.get("fromdate",str(datetime.date.today()-datetime.timedelta(7)))
        todate = req.GET.get("todate",str(datetime.date.today()))
        a["fromdate"] = fromdate
        a["todate"] = todate
        a["fields"] = field.objects.all()
        fid = req.GET.get("field_id","-1")
        a["fid"] = int(fid)
        if fid!="-1":
            bps = bigparty.objects.filter(thisfield_id=int(fid))
            a["bigparty"] = True
            a["bigparties"] = bps
            bpid = req.GET.get("bigparty_id","-1")
            a["bpid"] = int(bpid)
            if bpid!="-1":
                ps = party.objects.filter(thisbigparty_id=int(bpid))
                a["party"] = True
                a["parties"] = ps
                pid = req.GET.get("party_id","-1")
                a["pid"] = int(pid)
                if pid!="-1":
                    ms = manager.objects.filter(thisparty_id=int(pid))
                    a["manager"] = True
                    a["managers"] = ms
                    mid = req.GET.get("manager_id","-1")
                    a["mid"] = int(mid)
                    
        return render_to_response("managerYear.html",a)

@checkauth
def outputmanagerYear(req):
    def file_iterator(file_name, chunk_size=512):
        with open(file_name,"rb") as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break
    def writefile(items):
        w = Workbook()
        ws = w.add_sheet('sheet1')
        titles = [u"职场",u"大团",u"小团",u"经理",u"年化业绩"]
        for i in range(0,len(titles)):
            ws.write(0,i,titles[i])
        for i in range(0,len(items)):
            ws.write(i+1,0,items[i][1][1].thisparty.thisbigparty.thisfield.name)
            ws.write(i+1,1,items[i][1][1].thisparty.thisbigparty.name)
            ws.write(i+1,2,items[i][1][1].thisparty.name)
            ws.write(i+1,3,items[i][1][1].name)
            ws.write(i+1,4,"%.02f" % (items[i][1][0]))
        filename = ".//tmpfolder//" + str(datetime.datetime.now()).split(" ")[1].replace(":","").replace(".","") + ".xls"
        w.save(filename)
        return filename
    if not checkjurisdiction(req,"经理统计"):
        return render_to_response("jur.html",a)
    if req.method == "GET":
        ansmap = {}
        items = getitems(req,4)
        for item in items:
            incnt = 0.0
            if item.thisproduct.closedtype == 'm':
                incnt += float(item.money)*item.thisproduct.closedperiod/12
            elif item.thisproduct.closedtype == 'd':
                incnt += float(item.money)*item.thisproduct.closedperiod/365
            if item.thismanager.id in ansmap:
                ansmap[item.thismanager.id][0] += incnt
            else:
                ansmap[item.thismanager.id] = [incnt,item.thismanager]
        
        tmplist = sorted(ansmap.iteritems(),key=lambda asd:asd[1][0],reverse=True)
        
        the_file_name = writefile(tmplist)
        response = StreamingHttpResponse(file_iterator(the_file_name))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{0}"'.format("年化进账统计.xls")
        return response
        

@checkauth
def yearintocnt(req,a={},type_id=0):
    if not checkjurisdiction(req,"年化进账统计"):
        a = {'user':req.user}
        a["indexlist"] = getindexlist(req)
        return render_to_response("jur.html",a)
    if req.method == "GET":
        items = getitems(req,4)
        totalmoney = 0.0
        for item in items:
            if item.thisproduct.closedtype == 'm':
                totalmoney += float(item.money)*item.thisproduct.closedperiod/12
            elif item.thisproduct.closedtype == 'd':
                totalmoney += float(item.money)*item.thisproduct.closedperiod/365
        #a = {"user":req.user}
        fromdate = req.GET.get("fromdate",str(datetime.date.today()-datetime.timedelta(7)))
        todate = req.GET.get("todate",str(datetime.date.today()))
        a["totalmoney"] = "%.02f" % totalmoney
        a["cnt"] = len(items)
        a["fromdate"] = fromdate
        a["todate"] = todate
        if type_id==0:
            a["user"] = req.user
            a["indexlist"] = getindexlist(req)
            a["fields"] = field.objects.all()
            return render_to_response("yearintocnt.html",a)
        jsonstr = json.dumps(a,ensure_ascii=False)
        return HttpResponse(jsonstr,content_type='application/javascript')

@checkauth
def repaycnt(req,a={},type_id=0):
    if not checkjurisdiction(req,"返款统计"):
        a = {'user':req.user}
        a["indexlist"] = getindexlist(req)
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
        items = repayitem.objects.filter(repaydate__gte=fromdate,repaydate__lte=todate,status__gt=10)
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
            a["indexlist"] = getindexlist(req)
            a["fields"] = field.objects.all()
            return render_to_response("repaycnt.html",a)
        jsonstr = json.dumps(a,ensure_ascii=False)
        return HttpResponse(jsonstr,content_type='application/javascript')

@checkauth
def waitrepay(req,a={},type_id=0):
    if not checkjurisdiction(req,"待收查询"):
        a = {'user':req.user}
        a["indexlist"] = getindexlist(req)
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
            a["indexlist"] = getindexlist(req)
            a["fields"] = field.objects.all()
            return render_to_response("waitrepay.html",a)
        jsonstr = json.dumps(a,ensure_ascii=False)
        return HttpResponse(jsonstr,content_type='application/javascript')
    
@checkauth
def renewalRate(req):
    a = {'user':req.user}
    a["indexlist"] = getindexlist(req)
    if not checkjurisdiction(req,"经理统计"):
        return render_to_response("jur.html",a)
    if req.method == "GET":
        ansmap = {}
        items = GetEnddateItems(req)
        ansmap = {}
        for item in items:
            if item.renewal_son_id!=-1:
                newc = contract.objects.filter(id=item.renewal_son_id)[0]
                if item.thismanager.id in ansmap:
                    ansmap[item.thismanager.id][0] += float(newc.money)
                    ansmap[item.thismanager.id][1] += float(item.money)
                else:
                    ansmap[item.thismanager.id] = [float(newc.money),float(item.money),item.thismanager]
            else:
                if item.thismanager.id in ansmap:
                    ansmap[item.thismanager.id][1] += float(item.money)
                else:
                    ansmap[item.thismanager.id] = [0.0,float(item.money),item.thismanager]
        for item in ansmap:
            ansmap[item][0] = ansmap[item][0]/ansmap[item][1]
        tmplist = sorted(ansmap.iteritems(),key=lambda asd:asd[1][0],reverse=True)
        a["renewalRate"] = tmplist
        
        fromdate = req.GET.get("fromdate",str(datetime.date.today()-datetime.timedelta(7)))
        todate = req.GET.get("todate",str(datetime.date.today()))
        a["fromdate"] = fromdate
        a["todate"] = todate
        a["fields"] = field.objects.all()
        fid = req.GET.get("field_id","-1")
        a["fid"] = int(fid)
        if fid!="-1":
            bps = bigparty.objects.filter(thisfield_id=int(fid))
            a["bigparty"] = True
            a["bigparties"] = bps
            bpid = req.GET.get("bigparty_id","-1")
            a["bpid"] = int(bpid)
            if bpid!="-1":
                ps = party.objects.filter(thisbigparty_id=int(bpid))
                a["party"] = True
                a["parties"] = ps
                pid = req.GET.get("party_id","-1")
                a["pid"] = int(pid)
                if pid!="-1":
                    ms = manager.objects.filter(thisparty_id=int(pid))
                    a["manager"] = True
                    a["managers"] = ms
                    mid = req.GET.get("manager_id","-1")
                    a["mid"] = int(mid)
                    
        return render_to_response("renewalRate.html",a)
    
@checkauth
def outputrenewalRate(req):
    def file_iterator(file_name, chunk_size=512):
        with open(file_name,"rb") as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break
    def writefile(items):
        w = Workbook()
        ws = w.add_sheet('sheet1')
        titles = [u"职场",u"大团",u"小团",u"经理",u"续签率"]
        for i in range(0,len(titles)):
            ws.write(0,i,titles[i])
        for i in range(0,len(items)):
            ws.write(i+1,0,items[i][1][2].thisparty.thisbigparty.thisfield.name)
            ws.write(i+1,1,items[i][1][2].thisparty.thisbigparty.name)
            ws.write(i+1,2,items[i][1][2].thisparty.name)
            ws.write(i+1,3,items[i][1][2].name)
            ws.write(i+1,4,"%.02f" % (items[i][1][0]))
        filename = ".//tmpfolder//" + str(datetime.datetime.now()).split(" ")[1].replace(":","").replace(".","") + ".xls"
        w.save(filename)
        return filename
    if not checkjurisdiction(req,"经理统计"):
        return render_to_response("jur.html",a)
    if req.method == "GET":
        ansmap = {}
        items = GetEnddateItems(req)
        ansmap = {}
        for item in items:
            if item.renewal_son_id!=-1:
                newc = contract.objects.filter(id=item.renewal_son_id)[0]
                if item.thismanager.id in ansmap:
                    ansmap[item.thismanager.id][0] += float(newc.money)
                    ansmap[item.thismanager.id][1] += float(item.money)
                else:
                    ansmap[item.thismanager.id] = [float(newc.money),float(item.money),item.thismanager]
            else:
                if item.thismanager.id in ansmap:
                    ansmap[item.thismanager.id][1] += float(item.money)
                else:
                    ansmap[item.thismanager.id] = [0.0,float(item.money),item.thismanager]
        for item in ansmap:
            ansmap[item][0] = ansmap[item][0]/ansmap[item][1]
        tmplist = sorted(ansmap.iteritems(),key=lambda asd:asd[1][0],reverse=True)
        
        the_file_name = writefile(tmplist)
        response = StreamingHttpResponse(file_iterator(the_file_name))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{0}"'.format("续签率.xls")
        return response
    
@csrf_exempt
@checkauth
def cashCnt(req):
    a = {'user':req.user}
    a["indexlist"] = getindexlist(req)
    if not checkjurisdiction(req,"兑付统计"):
        return render_to_response("jur.html",a)
    if req.method == "GET":
        fromdate = req.GET.get("fromdate",str(datetime.date.today()))
        todate = req.GET.get("todate",str(datetime.date.today()+datetime.timedelta(7))) #未来一周
        cs = contract.objects.filter(enddate__gte=fromdate,enddate__lte=todate,status__gt=-1,renewal_son_id=-1)
        daymap = {}
        for item in cs:
            if item.enddate in daymap:
                daymap[item.enddate][0] += 1
                daymap[item.enddate][1] += float(item.money)
            else:
                daymap[item.enddate] = [1,float(item.money)]
        tmplist = sorted(daymap.iteritems(),key=lambda asd:asd[0])
        a["items"] = tmplist
        a["fromdate"] = fromdate
        a["todate"] = todate
        return render_to_response("dateCashCnt.html",a)       
    
@csrf_exempt
@checkauth
def daycashCnt(req,onedate):
    def file_iterator(file_name, chunk_size=512):
        with open(file_name,"rb") as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break
    def writefile(items):
        w = Workbook()
        ws = w.add_sheet('sheet1')
        titles = [u"到期日期",u"客户名",u"本金金额",u"理财经理",u"合同编号"]
        for i in range(0,len(titles)):
            ws.write(0,i,titles[i])
        for i in range(0,len(items)):
            ws.write(i+1,0,items[i].enddate)
            ws.write(i+1,1,items[i].client_name)
            ws.write(i+1,2,items[i].money)
            ws.write(i+1,3,items[i].thismanager.name)
            ws.write(i+1,4,items[i].number)
        filename = ".//tmpfolder//" + str(datetime.datetime.now()).split(" ")[1].replace(":","").replace(".","") + ".xls"
        w.save(filename)
        return filename
    
    a = {'user':req.user}
    a["indexlist"] = getindexlist(req)
    if not checkjurisdiction(req,"兑付统计"):
        return render_to_response("jur.html",a)
    items = contract.objects.filter(enddate=onedate,status__gt=-1,renewal_son_id=-1)
    if req.method == "POST":
        the_file_name = writefile(items)
        response = StreamingHttpResponse(file_iterator(the_file_name))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{0}"'.format("日期兑付表.xls")
        return response
    if req.method == "GET":
        a["items"] = items
        a["day"] = onedate
        return render_to_response("daycashCnt.html",a)
   
@checkauth
def managercashCnt(req):
    a = {'user':req.user}
    a["indexlist"] = getindexlist(req)
    if not checkjurisdiction(req,"兑付统计"):
        return render_to_response("jur.html",a)
    if req.method == "GET":
        ansmap = {}
        items = GetEnddateItems(req)
        for item in items:
            if item.renewal_son_id!=-1:
                continue
            if item.thismanager.id in ansmap:
                ansmap[item.thismanager.id][0] += 1
                ansmap[item.thismanager.id][1] += float(item.money)
            else:
                ansmap[item.thismanager.id] = [1,float(item.money),item.thismanager]
        
        tmplist = sorted(ansmap.iteritems(),key=lambda asd:asd[1][1],reverse=True)
        a["items"] = tmplist
        
        fromdate = req.GET.get("fromdate",str(datetime.date.today()-datetime.timedelta(7)))
        todate = req.GET.get("todate",str(datetime.date.today()))
        a["fromdate"] = fromdate
        a["todate"] = todate
        a["fields"] = field.objects.all()
        fid = req.GET.get("field_id","-1")
        a["fid"] = int(fid)
        if fid!="-1":
            bps = bigparty.objects.filter(thisfield_id=int(fid))
            a["bigparty"] = True
            a["bigparties"] = bps
            bpid = req.GET.get("bigparty_id","-1")
            a["bpid"] = int(bpid)
            if bpid!="-1":
                ps = party.objects.filter(thisbigparty_id=int(bpid))
                a["party"] = True
                a["parties"] = ps
                pid = req.GET.get("party_id","-1")
                a["pid"] = int(pid)
                if pid!="-1":
                    ms = manager.objects.filter(thisparty_id=int(pid))
                    a["manager"] = True
                    a["managers"] = ms
                    mid = req.GET.get("manager_id","-1")
                    a["mid"] = int(mid)
                    
        return render_to_response("managercashCnt.html",a)
    
@csrf_exempt
@checkauth
def managercashDetail(req,m_id):
    def file_iterator(file_name, chunk_size=512):
        with open(file_name,"rb") as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break
    def writefile(items):
        w = Workbook()
        ws = w.add_sheet('sheet1')
        titles = [u"到期日期",u"客户名",u"本金金额",u"理财经理",u"合同编号"]
        for i in range(0,len(titles)):
            ws.write(0,i,titles[i])
        for i in range(0,len(items)):
            ws.write(i+1,0,items[i].enddate)
            ws.write(i+1,1,items[i].client_name)
            ws.write(i+1,2,items[i].money)
            ws.write(i+1,3,items[i].thismanager.name)
            ws.write(i+1,4,items[i].number)
        filename = ".//tmpfolder//" + str(datetime.datetime.now()).split(" ")[1].replace(":","").replace(".","") + ".xls"
        w.save(filename)
        return filename
    
    a = {'user':req.user}
    a["indexlist"] = getindexlist(req)
    if not checkjurisdiction(req,"兑付统计"):
        return render_to_response("jur.html",a)
    if req.method == "GET":
        fromdate = req.GET.get("fromdate",str(datetime.date.today()))
        todate = req.GET.get("todate",str(datetime.date.today()+datetime.timedelta(7))) #未来一周
        items = contract.objects.filter(enddate__gte=fromdate,enddate__lte=todate,status__gt=-1,renewal_son_id=-1,thismanager_id=int(m_id))
        a["fromdate"] = fromdate
        a["todate"] = todate
        a["items"] = items
        a["mid"] = m_id
        return render_to_response("managercashDetail.html",a)
            
    if req.method == "POST":
        fromdate = req.POST.get("fromdate",str(datetime.date.today()))
        todate = req.POST.get("todate",str(datetime.date.today()+datetime.timedelta(7))) #未来一周
        items = contract.objects.filter(enddate__gte=fromdate,enddate__lte=todate,status__gt=-1,renewal_son_id=-1,thismanager_id=int(m_id))
        the_file_name = writefile(items)
        response = StreamingHttpResponse(file_iterator(the_file_name))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{0}"'.format("人员兑付表.xls")
        return response
@csrf_exempt
@checkauth
def guestCnt(req):
    a = {'user':req.user}
    a["indexlist"] = getindexlist(req)
    if not checkjurisdiction(req,"客户统计"):
        return render_to_response("jur.html",a)
    if req.method == "GET":
        fromdate = req.GET.get("fromdate",str(datetime.date.today()-datetime.timedelta(7)))
        todate = req.GET.get("todate",str(datetime.date.today()))
        allc = contract.objects.filter(enddate__gte=fromdate,enddate__lte=todate,status__gt=-1)
        guestmap = {}
        for eachc in allc:
            if eachc.client_idcard in guestmap:
                guestmap[eachc.client_idcard][0] += float(eachc.money)
            else:
                guestmap[eachc.client_idcard] = [float(eachc.money),eachc]
        guestlist = sorted(guestmap.items(), key=lambda d: d[1][0], reverse=True)
        a["guestlist"] = guestlist
        a["fromdate"] = fromdate
        a["todate"] = todate
        return render_to_response("guestcnt.html",a)
