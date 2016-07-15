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
from django.http import StreamingHttpResponse
from pyExcelerator import *

def filterRepayItems(fromdate,todate,contract_number,type_id):
    def item_compare(x,y):
        if y.repaydate>x.repaydate:
            return 1
        elif y.repaydate<x.repaydate:
            return -1
        return 0
    
    items = []
    try:
        contract_id = contract.objects.filter(number=contract_number)[0].id
    except:
        contract_id = -1
    if type_id=="1" or type_id=='4':
        if contract_id != -1:
            try:
                items = repayitem.objects.filter(repaydate__gte=fromdate,repaydate__lte=todate,
                        thiscontract_id__exact=contract_id,status__gt=-1,status__lt=10)
            except:
                items = []
        elif contract_number=="":
            items = repayitem.objects.filter(repaydate__gte=fromdate,repaydate__lte=todate,status__gt=-1,status__lt=10)
    elif type_id=="2":
        if contract_id != -1:
            items = repayitem.objects.filter(repaydate__gte=fromdate,repaydate__lte=todate,
                    thiscontract_id__exact=contract_id,repaytype__gte=2,status__exact=1)
        elif contract_number=="":
            items = repayitem.objects.filter(repaydate__gte=fromdate,repaydate__lte=todate,
                    repaytype__gte=2,status__exact=1)
    elif type_id=="3":
        if contract_id != -1:
            items = list(repayitem.objects.filter(repaydate__gte=fromdate,repaydate__lte=todate,
                    thiscontract_id__exact=contract_id,repaytype__gte=2,status__exact=1))
            tmpitem = repayitem.objects.filter(repaydate__gte=fromdate,repaydate__lte=todate,
                    thiscontract_id__exact=contract_id,repaytype__gte=2,status__exact=3)
            items.extend(list(tmpitem))
        elif contract_number=="":
            items = list(repayitem.objects.filter(repaydate__gte=fromdate,repaydate__lte=todate,
                    repaytype__gte=2,status__exact=3))
            tmpitem = repayitem.objects.filter(repaydate__gte=fromdate,repaydate__lte=todate,repaytype__gte=2,status__exact=1)
            items.extend(list(tmpitem))
    elif type_id=="5":
        if contract_id != -1:
            items = list(repayitem.objects.filter(repaydate__gte=fromdate,repaydate__lte=todate,
                    thiscontract_id__exact=contract_id,repaytype=1,status__exact=1))
            tmpitem = repayitem.objects.filter(repaydate__gte=fromdate,repaydate__lte=todate,
                    thiscontract_id__exact=contract_id,repaytype=1,status__exact=3)
            items.extend(list(tmpitem))
        elif contract_number=="":
            items = list(repayitem.objects.filter(repaydate__gte=fromdate,repaydate__lte=todate,
                    repaytype=1,status__exact=3))
            tmpitem = repayitem.objects.filter(repaydate__gte=fromdate,repaydate__lte=todate,repaytype=1,status__exact=1)
            items.extend(list(tmpitem))
    return sorted(items,cmp=item_compare)
                
@checkauth
def outputfile(req,type_id):
    a = {'user':req.user}
    a["indexlist"] = getindexlist(req)
    if not checkjurisdiction(req,"还款查询"):
        return render_to_response("jur.html",a)
    
    def item_compare(x,y):
        if y.repaydate>x.repaydate:
            return 1
        elif y.repaydate<x.repaydate:
            return -1
        return 0
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
        titles = [u"收款账户列",u"收款账户名列",u"转账金额列",u"备注列",u"收款银行列",u"收款银行支行列",u"收款省/直辖市列",u"收款市县列"]
        for i in range(0,len(titles)):
            ws.write(0,i,titles[i])
        for i in range(0,len(items)):
            ws.write(i+1,0,items[i].thiscontract.bank_card)
            ws.write(i+1,1,items[i].thiscontract.client_name)
            ws.write(i+1,2,"%0.2f" % float(items[i].repaymoney))
            ws.write(i+1,3,items[i].thiscontract.comment)
            ws.write(i+1,4,items[i].thiscontract.bank)
            ws.write(i+1,5,items[i].thiscontract.subbranch)
            ws.write(i+1,6,items[i].thiscontract.province)
            ws.write(i+1,7,items[i].thiscontract.city)
        filename = ".//tmpfolder//" + str(datetime.datetime.now()).split(" ")[1].replace(":","").replace(".","") + ".xls"
        print filename
        w.save(filename)
        return filename
        
    if req.method == "GET":
        fromdate = req.GET.get("fromdate",str(datetime.date.today()))
        todate = req.GET.get("todate",str(datetime.date.today()+datetime.timedelta(7))) #下一周
        contract_number = req.GET.get("contract_id","")
        sorteditems = filterRepayItems(fromdate,todate,contract_number,type_id)
        
        if type_id=='3':
            fileline = "本金转账数据.xls"
        elif type_id=='5':
            fileline = "利息转账数据.xls"
        else:
            fileline = "转账数据.xls"
            
        the_file_name = writefile(sorteditems)
        response = StreamingHttpResponse(file_iterator(the_file_name))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{0}"'.format(fileline)
        return response
    
@checkauth
def outhiddenfile(req):
    a = {'user':req.user}
    a["indexlist"] = getindexlist(req)
    if not checkjurisdiction(req,"还款查询"):
        return render_to_response("jur.html",a)
    
    def item_compare(x,y):
        if y.repaydate>x.repaydate:
            return 1
        elif y.repaydate<x.repaydate:
            return -1
        return 0
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
        titles = [u"收款账户列",u"收款账户名列",u"转账金额列",u"备注列",u"收款银行列",u"收款银行支行列",u"收款省/直辖市列",u"收款市县列"]
        for i in range(0,len(titles)):
            ws.write(0,i,titles[i])
        for i in range(0,len(items)):
            ws.write(i+1,0,items[i].thiscontract.bank_card)
            ws.write(i+1,1,items[i].thiscontract.client_name)
            ws.write(i+1,2,"%0.2f" % float(items[i].repaymoney))
            ws.write(i+1,3,items[i].thiscontract.comment)
            ws.write(i+1,4,items[i].thiscontract.bank)
            ws.write(i+1,5,items[i].thiscontract.subbranch)
            ws.write(i+1,6,items[i].thiscontract.province)
            ws.write(i+1,7,items[i].thiscontract.city)
        filename = ".//tmpfolder//" + str(datetime.datetime.now()).split(" ")[1].replace(":","").replace(".","") + ".xls"
        print filename
        w.save(filename)
        return filename
        
    if req.method == "GET":
        fromdate = req.GET.get("fromdate",str(datetime.date.today()))
        todate = req.GET.get("todate",str(datetime.date.today()+datetime.timedelta(7))) #下一周
        contract_number = req.GET.get("contract_id","")
        items = repayitem.objects.filter(repaydate__gte=fromdate,repaydate__lte=todate,status__gte=10)
        sorteditems = sorted(items,cmp=item_compare)
        the_file_name = writefile(sorteditems)
        response = StreamingHttpResponse(file_iterator(the_file_name))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{0}"'.format("测试转账数据.xls")
        return response    
    
    
@csrf_exempt
@checkauth
def changejur(req):
    a = {'user':req.user}
    a["indexlist"] = getindexlist(req)
    if not checkjurisdiction(req,"账户管理"):
        return render_to_response("jur.html",a)
    
    a['users'] = users.objects.all()
    if req.method == 'GET':
        form = ChangeJurForm()
        a["form"] = form
        return render_to_response('changejur.html', a)
    else:
        form = ChangeJurForm(req.POST)
        if form.is_valid():
            user_id = req.POST.get("user_id","")
            thisuser = users.objects.filter(id=int(user_id))
            if not thisuser:
                return render_to_response("home.html",a)
            check_list = req.POST.getlist("jur")
            jur = 0
            for item in check_list:
                jur += int(item)
            thisuser = thisuser[0]
            thisuser.jurisdiction = jur
            thisuser.save()
            a["change_succ"] = "true"
            a["form"] = form
            return render_to_response('changejur.html', a)
        else:
            a["form"] = form
            return render_to_response('changejur.html', a)
        
@checkauth
def changecon(req):
    a = {'user':req.user}
    a["indexlist"] = getindexlist(req)
    if not checkjurisdiction(req,"新增合同"):
        return render_to_response("jur.html",a)
    if req.method == "GET":
        number = req.GET.get("number","")
        if number=="":
            allc = contract.objects.filter(operator_id=req.user.id,status__lte=2,status__gte=1)
        else:
            allc = contract.objects.filter(operator_id=req.user.id,number=number,status__lte=2,status__gte=1)
        a["contracts"] = allc
        return render_to_response("changecon.html",a)
    
@checkauth
def showmanager(req,mid):
    a = {'user':req.user}
    a["indexlist"] = getindexlist(req)
    if req.method == "GET":
        allc = contract.objects.filter(thismanager_id=int(mid))
        a["contracts"] = allc
        return render_to_response("manager_contract.html",a)

@csrf_exempt
@checkauth
def repayinterest(req):
    a = {'user':req.user}
    a["indexlist"] = getindexlist(req)
    if not checkjurisdiction(req,"还款确认"):
        return render_to_response("jur.html",a)
    if req.method == "POST":
        fromdate = req.POST.get("fromdate",str(datetime.date.today()))
        todate = req.POST.get("todate",str(datetime.date.today()+datetime.timedelta(7))) #下一周
        contract_number = req.POST.get("contract_id","")
        
        sorteditems = filterRepayItems(fromdate,todate,contract_number,"5") 
        a["message"] = "true"
        failitems = []
        for thisitem in reversed(sorteditems):
            print thisitem.status
            if thisitem.status==1 or thisitem.status==3:
                restitems = repayitem.objects.filter(thiscontract_id=thisitem.thiscontract.id,repaydate__lt=thisitem.repaydate)
                thisrepaysuc = True
                for restitem in restitems:
                    if restitem.status==1:
                        a["info"] = "前期款项还未还"
                        print "false"
                        a["message"] = "false"
                        thisrepaysuc = False
                        failitems.append(thisitem)
                        break
                if thisrepaysuc:
                    thisitem.status += 1
                    thisitem.save()
                    thislog = loginfo(info="repay with %d of contract number=%s" % (thisitem.id,thisitem.thiscontract.number),time=str(datetime.datetime.now()),thisuser=req.user)
                    thislog.save()
                        
       
        a["repayitems"] = failitems
        a["type_id"] = "5"
        a["fromdate"] = fromdate
        a["todate"] = todate
        a["number"] = contract_number
        
        return render_to_response("queryrepayitems.html",a)
