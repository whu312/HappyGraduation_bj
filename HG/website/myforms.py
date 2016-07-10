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
from django import forms
from django.template import *

jurlist = ["新增合同","合同查询","合同审核","审核回退","最终审核","合同终止","还款查询","到期续单",
        "还款确认","全部还款查询","产品管理","经理管理","团队管理","职场管理","账户管理",
        "密码修改","系统日志","还款计划","进账统计","年化进账统计","返款统计","待收查询","人员结构",
        "经理统计","续单统计","兑付统计","合同导出"]
def getjurtuple(onelist):
    j = 1
    jlist = []
    for item in jurlist:
        jlist.append((str(j),item))
        j = j<<1
    return tuple(jlist)

class ChangepwdForm(forms.Form):
    oldpassword = forms.CharField(
        required=True,
        label=u"原密码",
        error_messages={'required': u'请输入原密码'},
        widget=forms.PasswordInput(
            attrs={
                'placeholder':u"原密码",
            }
        ),
    ) 
    newpassword1 = forms.CharField(
        required=True,
        label=u"新密码",
        error_messages={'required': u'请输入新密码'},
        widget=forms.PasswordInput(
            attrs={
                'placeholder':u"新密码",
            }
        ),
    )
    newpassword2 = forms.CharField(
        required=True,
        label=u"确认密码",
        error_messages={'required': u'请再次输入新密码'},
        widget=forms.PasswordInput(
            attrs={
                'placeholder':u"确认密码",
            }
        ),
    )
    def clean(self):
        if not self.is_valid():
            raise forms.ValidationError(u"所有项都为必填项")
        elif self.cleaned_data['newpassword1'] <> self.cleaned_data['newpassword2']:
            raise forms.ValidationError(u"两次输入的新密码不一样")
        else:
            cleaned_data = super(ChangepwdForm, self).clean()
        return cleaned_data

class NewContractForm(forms.Form):
    number = forms.CharField(
        required=True,
        label=u"合同编号",
        error_messages={'required': u'请输入合同编号'},
        widget=forms.TextInput(
            attrs={
                'placeholder':u"合同编号",
            }
        ),
    ) 
    client_name = forms.CharField(
        required=True,
        label=u"客户姓名",
        error_messages={'required': u'请输入客户姓名'},
        widget=forms.TextInput(
            attrs={
                'placeholder':u"客户姓名",
            }
        ),
    )
    client_idcard = forms.CharField(
        required=True,
        label=u"客户身份证",
        error_messages={'required': u'请输入客户身份证'},
        widget=forms.TextInput(
            attrs={
                'placeholder':u"客户身份证",
            }
        ),
    )
    address = forms.CharField(
        required=True,
        label=u"客户地址",
        error_messages={'required': u'请输入客户地址'},
        widget=forms.TextInput(
            attrs={
                'placeholder':u"家庭地址",
            }
        ),
    )
    bank = forms.CharField(
        required=True,
        label=u"开户行",
        error_messages={'required': u'请输入开户行'},
        widget=forms.TextInput(
            attrs={
                'placeholder':u"开户行",
            }
        ),
    )
    subbranch = forms.CharField(
        required=True,
        label=u"支行",
        error_messages={'required': u'请输入银行支行'},
        widget=forms.TextInput(
            attrs={
                'placeholder':u"支行",
            }
        ),
    )
    province = forms.CharField(
        required=True,
        label=u"收款省/直辖市",
        error_messages={'required': u'请输入收款省/直辖市'},
        widget=forms.TextInput(
            attrs={
                'placeholder':u"省/直辖市",
            }
        ),
    )
    city = forms.CharField(
        required=True,
        label=u"收款市/县",
        error_messages={'required': u'请输入收款市县'},
        widget=forms.TextInput(
            attrs={
                'placeholder':u"收款市县",
            }
        ),
    )
    bank_card = forms.CharField(
        required=True,
        label=u"银行卡号",
        error_messages={'required': u'请输入银行卡号'},
        widget=forms.TextInput(
            attrs={
                'placeholder':u"银行卡号",
            }
        ),
    )
    money = forms.CharField(
        required=True,
        label=u"金额",
        error_messages={'required': u'请输入金额'},
        widget=forms.TextInput(
            attrs={
                'placeholder':u"金额",
            }
        ),
    )
    startdate = forms.CharField(
        required=True,
        label=u"开始日期",
        error_messages={'required': u'请输入开始日期'},
        widget=forms.TextInput(
            attrs={
                "onClick":"WdatePicker()",
            }
        ),
    )
    enddate = forms.CharField(
        required=True,
        label=u"截止日期",
        error_messages={'required': u'请输入截止日期'},
        widget=forms.TextInput(
            attrs={
                "onClick":"WdatePicker()",
            }
        ),
    )
    factorage = forms.CharField(
        required=True,
        label=u"手续费",
        error_messages={'required': u'请输入手续费'},
        widget=forms.TextInput(
            attrs={
                'placeholder':u"手续费",
            }
        ),
    )
    comment = forms.CharField(
        required=False,
        label=u"备注",
        error_messages={'required': u'请输入备注'},
        widget=forms.TextInput(
            attrs={
                'placeholder':u"备注",
            }
        ),
    )
    def clean(self):
        if not self.is_valid():
            raise forms.ValidationError(u"所有项都为必填项")
        elif len(self.cleaned_data['number']) <> 10:
            raise forms.ValidationError(u"合同号要求10位")
        elif len(self.cleaned_data['client_idcard']) <> 18:
            raise forms.ValidationError(u"请输入正确的身份证号")
        else:
            cleaned_data = super(NewContractForm, self).clean()
        return cleaned_data

class NewFieldForm(forms.Form):
    name = forms.CharField(
        required=True,
        label=u"职场名称",
        error_messages={'required': u'请输入职场名称'},
        widget=forms.TextInput(
            attrs={
                'placeholder':u"职场名称",
            }
        ),
    ) 
    address = forms.CharField(
        required=True,
        label=u"职场地址",
        error_messages={'required': u'请输入职场地址'},
        widget=forms.TextInput(
            attrs={
                'placeholder':u"职场地址",
            }
        ),
    )
    tel = forms.CharField(
        required=True,
        label=u"职场电话",
        error_messages={'required': u'请输入职场电话'},
        widget=forms.TextInput(
            attrs={
                'placeholder':u"职场电话",
            }
        ),
    )
    def clean(self):
        if not self.is_valid():
            raise forms.ValidationError(u"所有项都为必填项")
        else:
            cleaned_data = super(NewFieldForm, self).clean()
        return cleaned_data

class NewPartyForm(forms.Form):
    name = forms.CharField(
        required=True,
        label=u"团队名称",
        error_messages={'required': u'请输入团队名称'},
        widget=forms.TextInput(
            attrs={
                'placeholder':u"团队名称",
            }
        ),
    ) 
    def clean(self):
        if not self.is_valid():
            raise forms.ValidationError(u"所有项都为必填项")
        else:
            cleaned_data = super(NewPartyForm, self).clean()
        return cleaned_data

class NewManagerForm(forms.Form):
    name = forms.CharField(
        required=True,
        label=u"经理姓名",
        error_messages={'required': u'请输入经理姓名'},
        widget=forms.TextInput(
            attrs={
                'placeholder':u"经理姓名",
            }
        ),
    )
    number = forms.CharField(
        required=True,
        label=u"经理编号",
        error_messages={'required': u'请输入经理编号'},
        widget=forms.TextInput(
            attrs={
                'placeholder':u"经理编号",
            }
        ),
    ) 
    tel = forms.CharField(
        required=True,
        label=u"电话",
        error_messages={'required': u'请输入经理联系方式'},
        widget=forms.TextInput(
            attrs={
                'placeholder':u"经理电话",
            }
        ),
    ) 
    def clean(self):
        if not self.is_valid():
            raise forms.ValidationError(u"所有项都为必填项")
        else:
            cleaned_data = super(NewManagerForm, self).clean()
        return cleaned_data
class NewProductForm(forms.Form):
    name = forms.CharField(
        required=True,
        label=u"产品名称",
        error_messages={'required': u'请输入产品名称'},
        widget=forms.TextInput(
            attrs={
                'placeholder':u"产品名称",
            }
        ),
    )
    rate = forms.FloatField(
        required=True,
        label=u"年化收益",
        error_messages={'required': u'请输入年化收益%'},
        widget=forms.TextInput(
            attrs={
                'placeholder':u"年化收益",
            }
        ),
    ) 
    closedtype = forms.ChoiceField(
        required=True,
        label=u"封闭类型",
        error_messages={'required': u'请选择封闭类型'},
        choices=(('m',u"月"),("d",u"天")),
    ) 
    closedperiod = forms.IntegerField(
        required=True,
        label=u"封闭期",
        error_messages={'required': u'请输入封闭期'},
        widget=forms.TextInput(
            attrs={
                'placeholder':u"封闭期",
            }
        ),
    )
    def clean(self):
        if not self.is_valid():
            raise forms.ValidationError(u"所有项都为必填项")
        else:
            cleaned_data = super(NewProductForm, self).clean()
        return cleaned_data

class NewUserForm(forms.Form):
    username = forms.CharField(
        required=True,
        label=u"登陆名",
        error_messages={'required': u'请输入登录名'},
        widget=forms.TextInput(
            attrs={
                'placeholder':u"登录名",
            }
        ),
    )
    password = forms.CharField(
        required=True,
        label=u"密码",
        error_messages={'required': u'请输入密码'},
        widget=forms.PasswordInput(
            attrs={
                'placeholder':u"密码",
            }
        ),
    )
    name = forms.CharField(
        required=True,
        label=u"姓名",
        error_messages={'required': u'请输入姓名'},
        widget=forms.TextInput(
            attrs={
                'placeholder':u"姓名",
            }
        ),
    )
    email = forms.EmailField(
        required=True,
        label=u"邮箱",
        error_messages={'required': u'请输入邮箱'},
        widget=forms.TextInput(
            attrs={
                'placeholder':u"邮箱",
            }
        ),
    )
    position = forms.CharField(
        required=True,
        label=u"职位",
        error_messages={'required': u'请输入职位'},
        widget=forms.TextInput(
            attrs={
                'placeholder':u"职位",
            }
        ),
    )
    jur = forms.MultipleChoiceField(
        required=True,
        label=u"权限",
        error_messages={'required': u'请选择权限'},
        choices=getjurtuple(jurlist), 
        widget=forms.CheckboxSelectMultiple(),
    )
    def clean(self):
        if not self.is_valid():
            raise forms.ValidationError(u"所有项都为必填项")
        else:
            cleaned_data = super(NewUserForm, self).clean()
        return cleaned_data
    
class ChangeJurForm(forms.Form):
    jur = forms.MultipleChoiceField(
        required=True,
        label=u"权限",
        error_messages={'required': u'请选择权限'},
        choices=getjurtuple(jurlist), 
        widget=forms.CheckboxSelectMultiple(),
    )
    def clean(self):
        if not self.is_valid():
            raise forms.ValidationError(u"所有项都为必填项")
        else:
            cleaned_data = super(ChangeJurForm, self).clean()
        return cleaned_data
