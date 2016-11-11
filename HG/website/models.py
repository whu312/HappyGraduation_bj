from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class users(models.Model):
    name = models.CharField(max_length = 128)
    username = models.CharField(max_length = 128)
    position = models.CharField(max_length = 128)
    jurisdiction = models.IntegerField()
    thisuser = models.ForeignKey(User)
class cycle(models.Model):
    name = models.CharField(max_length = 128)
    cycletype = models.IntegerField()
class product(models.Model):
    name = models.CharField(max_length = 128)
    rate = models.CharField(max_length = 16)
    repaycycle = models.ForeignKey(cycle)
    closedtype = models.CharField(max_length = 16)
    closedperiod = models.IntegerField()
class field(models.Model):
    name = models.CharField(max_length = 128)
    address = models.CharField(max_length = 128)
    tel = models.CharField(max_length = 128)
class bigparty(models.Model):
    name = models.CharField(max_length = 128)
    thisfield = models.ForeignKey(field)
class party(models.Model):
    name = models.CharField(max_length = 128)
    thisbigparty = models.ForeignKey(bigparty)
class manager(models.Model):
    name = models.CharField(max_length = 128)
    tel = models.CharField(max_length = 32)
    number = models.CharField(max_length = 128)
    thisparty = models.ForeignKey(party) 
class contract(models.Model):
    number = models.CharField(max_length = 128)
    client_name = models.CharField(max_length = 128)
    client_idcard = models.CharField(max_length = 128)
    address = models.CharField(max_length = 256)
    bank = models.CharField(max_length = 128)
    bank_card = models.CharField(max_length = 128)
    subbranch = models.CharField(max_length = 128)
    province = models.CharField(max_length = 128)
    city = models.CharField(max_length = 128)
    money = models.CharField(max_length = 128)
    thisproduct = models.ForeignKey(product)
    startdate = models.CharField(max_length = 32)
    enddate = models.CharField(max_length = 32)
    factorage = models.CharField(max_length = 32)
    comment = models.CharField(max_length = 512)
    status = models.IntegerField()
    thismanager = models.ForeignKey(manager)
    renewal_father_id = models.IntegerField()
    renewal_son_id = models.IntegerField()
    operator = models.ForeignKey(User)
class repayitem(models.Model):
    repaydate = models.CharField(max_length = 32)
    repaymoney = models.CharField(max_length = 128)
    repaytype = models.IntegerField()
    status = models.IntegerField()
    thiscontract = models.ForeignKey(contract)
class loginfo(models.Model):
    info = models.CharField(max_length = 1024)
    time = models.CharField(max_length = 128)
    thisuser = models.ForeignKey(User) 
class MinShowMoney(models.Model):
    money = models.IntegerField()
