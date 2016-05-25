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
    if req.method == 'POST':
        user_id = req.POST.get("user_id","")
        thisuser = users.objects.filter(thisuser_id=int(user_id))[0]
        curuser = thisuser.thisuser
        thisuser.delete()
        curuser.delete()
        return render_to_response('home.html', a)

@csrf_exempt
@checkauth
def passwd(request):
    a = {'user':request.user}
    if not checkjurisdiction(request,"密码修改"):
        return render_to_response("jur.html",a)
    
    if request.method == 'GET':
        form = ChangepwdForm()
        return render_to_response('passwd.html', RequestContext(request, {'form': form,'user':request.user}))
    else:
        form = ChangepwdForm(request.POST)
        if form.is_valid():
            username = request.user.username
            oldpassword = request.POST.get('oldpsw', '')
            user = auth.authenticate(username=username, password=oldpassword)
            if user is not None and user.is_active:
                newpassword = request.POST.get('newpsw1', '')
                user.set_password(newpassword)
                user.save()
                return render_to_response('passwd.html', RequestContext(request,{'changepwd_success':True,"user":request.user}))
            else:
                return render_to_response('passwd.html', RequestContext(request, {'form': form,'oldpassword_is_wrong':True,"user":request.user}))
        else:
            return render_to_response('passwd.html', RequestContext(request, {'form': form,"user":request.user}))
