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
                        thiscontract_id__exact=contract_id,status__gt=-1)
            except:
                items = []
        elif contract_number=="":
            items = repayitem.objects.filter(repaydate__gte=fromdate,repaydate__lte=todate,status__gt=-1)
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
                    thiscontract_id__exact=contract_id,status__exact=1))
            tmpitem = repayitem.objects.filter(repaydate__gte=fromdate,repaydate__lte=todate,
                    thiscontract_id__exact=contract_id,status__exact=3)
            items.extend(list(tmpitem))
        elif contract_number=="":
            items = list(repayitem.objects.filter(repaydate__gte=fromdate,repaydate__lte=todate,
                    status__exact=3))
            tmpitem = repayitem.objects.filter(repaydate__gte=fromdate,repaydate__lte=todate,status__exact=1)
            items.extend(list(tmpitem))
    return sorted(items,cmp=item_compare)
                
@checkauth
def outputfile(req,type_id):
    a = {'user':req.user}
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
        
        the_file_name = writefile(sorteditems)
        response = StreamingHttpResponse(file_iterator(the_file_name))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{0}"'.format("转账数据.xls")
        return response
