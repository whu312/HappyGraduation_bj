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
from myforms import *

def getJurisdictions(onelist=jurlist):
    j = 1
    ans = {}
    for line in onelist:
        ans[line] = j
        j = j << 1
    return ans

def checkjurisdiction(req,page):
    thisuser = users.objects.filter(thisuser_id=req.user.id)[0]
    limits = 0
    jurisdictions = getJurisdictions()
    if page in jurisdictions:
        limits = jurisdictions[page]
    if thisuser.jurisdiction & limits:
        return True
    return False

def checkauth(func):
    def _checkauth(req,*c):
        if req.user.is_authenticated():
            return func(req,*c)
        return render_to_response("index.html")
    return _checkauth

'''
add user
'''
def test(req):
    if req.method == 'GET':
        name = req.GET.get("name",'')
        email = req.GET.get("email",'')
        passwd = req.GET.get("password",'')
        userexist = User.objects.filter(username = name)
        if not userexist:
            user = User(username = name,email = email)
            user.set_password(passwd)
            user.save()
            mylimit = 2**31-1
            oneuser = users(name=name,username=name,jurisdiction=mylimit,thisuser=user)
            oneuser.save()
        else:
            mylimit = 2**31-1
            oneuser = users(name=name,username=name,jurisdiction=mylimit,thisuser=userexist[0])
            oneuser.save()
        return HttpResponse("add user ok")

@csrf_exempt
def login(req):
    if req.method == 'POST':
        name = req.POST.get('lname', '')
        passwd = req.POST.get('lpasswd', '')
        wizard = auth.authenticate(username = name, password = passwd)
        if wizard:
            auth.login(req, wizard)
            a = {}
            if req.user.is_authenticated():
                a['user'] = req.user
                a["indexlist"] = getindexlist(req)
            return render_to_response("home.html",a)
        else:
            a = {}
            a['logfail'] = True
            a['lname'] = name
            a['lpasswd'] = passwd
            return render_to_response("index.html",a)
        
def logout(req):
    auth.logout(req)
    return render_to_response("index.html")

@csrf_exempt
@checkauth
def userctl(req):
    '''
    a['user'] = req.user
    jur = getJurisdictions()
    jur = sorted(jur.iteritems(), key=lambda d:d[1], reverse = False)
    a["jur"] = jur
    a['users'] = users.objects.all()
    return render_to_response("userctl.html",a)
    '''
    a = {'user':req.user}
    a["indexlist"] = getindexlist(req)
    if not checkjurisdiction(req,"账户管理"):
        return render_to_response("jur.html",a)
    
    a['users'] = users.objects.all()
    if req.method == 'GET':
        form = NewUserForm()
        a["form"] = form
        return render_to_response('userctl.html', a)
    else:
        form = NewUserForm(req.POST)
        if form.is_valid():
            username = req.POST.get("username","")
            password = req.POST.get('password', '')
            name = req.POST.get("name","")
            email = req.POST.get("email","")
            position = req.POST.get("position","")
            check_list = req.POST.getlist("jur")
            jur = 0
            for item in check_list:
                jur += int(item)
            userexist = User.objects.filter(username = username)
            if not userexist:
                user = User(username = username, email = email)
                user.set_password(password)
                user.save()
                oneuser = users(name=name,username=username,jurisdiction=jur,thisuser=user)
                oneuser.save()
                a["add_succ"] = True
                a["form"] = form
                return render_to_response('userctl.html', a)
            else:
                a["form"] = form
                a["exist"] = True
                return render_to_response('userctl.html', a)
        else:
            a["form"] = form
            return render_to_response('userctl.html', a)

@csrf_exempt
@checkauth
def deleteuser(req):
    a = {'user':req.user}
    a["indexlist"] = getindexlist(req)
    if req.method == 'POST':
        user_id = req.POST.get("user_id","")
        try:
            thisuser = users.objects.filter(id=int(user_id))[0]
        except:
            pass
        try:
            curuser = thisuser.thisuser
        except:
            curuser = None
        if thisuser:
            thisuser.delete()
        if curuser:
            curuser.delete()
        return render_to_response('home.html', a)

@csrf_exempt
@checkauth
def passwd(request):
    a = {'user':request.user}
    a["indexlist"] = getindexlist(request)
    if not checkjurisdiction(request,"密码修改"):
        return render_to_response("jur.html",a)
    
    if request.method == 'GET':
        form = ChangepwdForm()
        a["form"] = form
        return render_to_response('passwd.html', a)
    else:
        form = ChangepwdForm(request.POST)
        a["form"] = form
        if form.is_valid():
            username = request.user.username
            oldpassword = request.POST.get('oldpassword', '')
            
            user = auth.authenticate(username=username, password=oldpassword)
            
            if user is not None and user.is_active:
                newpassword = request.POST.get('newpassword1', '')
                user.set_password(newpassword)
                user.save()
                a["changepwd_success"] = True
                return render_to_response('passwd.html', a)
            else:
                a["oldpassword_is_wrong"] = True
                return render_to_response('passwd.html', a)
        else:
            return render_to_response('passwd.html', a)
        
indexlist = [("合同管理",["新增合同","合同审核","全部合同查询","合同总数审核","合同修改"]),
             ("还款管理",["还款查询","到期续单","还款确认","全部还款查询"]),
             ("参数设置",["产品管理","经理管理","团队管理","职场管理","人员结构"]),
             ("系统设置",["账户管理","密码修改","系统日志"]),
             ("统计功能",["还款计划","进账统计","年化进账统计","返款统计","待收查询"])]

def getindexlist(req):
    thisuser = users.objects.filter(thisuser_id=req.user.id)[0]
    limits = 0
    anslist = []
    if thisuser.jurisdiction & int("10111",2):
        tmplist = []
        if thisuser.jurisdiction & int("1",2):
            tmplist.append(("新增合同","/newcontract"))
        if thisuser.jurisdiction & int("100",2):
            tmplist.append(("合同审核","/checkcontracts"))
        if thisuser.jurisdiction & int("10",2):
            tmplist.append(("全部合同查询","/querycontracts"))
        if thisuser.jurisdiction & int("10000",2):
            tmplist.append(("合同总数审核","/lastcheck"))
        if thisuser.jurisdiction & int("1",2):
            tmplist.append(("合同修改","/changecon"))
        anslist.append(("合同管理",tmplist))
    if thisuser.jurisdiction & int("1111000000",2):
        tmplist = []
        if thisuser.jurisdiction & int("1000000",2):
            tmplist.append(("还款查询","/queryrepayitems/1"))
        if thisuser.jurisdiction & int("10000000",2):
            tmplist.append(("到期续单","/queryrepayitems/2"))
        if thisuser.jurisdiction & int("100000000",2):
            tmplist.append(("还款确认","/queryrepayitems/3"))
        if thisuser.jurisdiction & int("1000000000",2):
            tmplist.append(("全部还款查询","/queryrepayitems/4"))     
        anslist.append(("还款管理",tmplist))
    if thisuser.jurisdiction & int("10000000011110000000000",2):
        tmplist = []
        if thisuser.jurisdiction & int("10000000000",2):
            tmplist.append(("产品管理","/newproduct"))
        if thisuser.jurisdiction & int("100000000000",2):
            tmplist.append(("经理管理","/newmanager"))
        if thisuser.jurisdiction & int("1000000000000",2):
            tmplist.append(("团队管理","/newbigparty"))
        if thisuser.jurisdiction & int("10000000000000",2):
            tmplist.append(("职场管理","/newfield"))
        if thisuser.jurisdiction & int("10000000000000000000000",2):
            tmplist.append(("人员结构","/construct"))
        anslist.append(("参数设置",tmplist))
    if thisuser.jurisdiction & int("11100000000000000",2):
        tmplist = []
        if thisuser.jurisdiction & int("100000000000000",2):
            tmplist.append(("账号管理","/settings"))
        if thisuser.jurisdiction & int("1000000000000000",2):
            tmplist.append(("密码修改","/passwd"))
        if thisuser.jurisdiction & int("10000000000000000",2):
            tmplist.append(("系统日志","/log"))
        anslist.append(("系统设置",tmplist))
    if thisuser.jurisdiction & int("1111100000000000000000",2):
        tmplist = []
        if thisuser.jurisdiction & int("100000000000000000",2):
            tmplist.append(("还款计划","/repayplan"))
        if thisuser.jurisdiction & int("1000000000000000",2):
            tmplist.append(("进账统计","/intocnt"))
        if thisuser.jurisdiction & int("10000000000000000",2):
            tmplist.append(("年化进账统计","/yearintocnt"))
        if thisuser.jurisdiction & int("1000000000000000",2):
            tmplist.append(("返款统计","/repaycnt"))
        if thisuser.jurisdiction & int("10000000000000000",2):
            tmplist.append(("待收查询","/waitrepay"))
        anslist.append(("统计功能",tmplist))
    return anslist
