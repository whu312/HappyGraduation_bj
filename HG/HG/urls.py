"""HG URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
import settings
from website.views import *
from website.users import *
from website.statistics import *
from website.newadd import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^cleanall$', cleanall),
    url(r'^html$', testhtml),
    url(r'^test$', test),
    url(r'^testcycle$', addcycle),
    url(r'^$', index),
    url(r'^login$', login),
    url(r'^logout$', logout),
    url(r'^newcontract$', newcontract),
    url(r'^checknumber$', checknumber),
    url(r'^statuscontract$', statuscontract),
    url(r'^statusrepayitem/([0-9]+)/$', statusrepayitem),
    url(r'^renewalcontract/([0-9]+)/$', renewalcontract),
    url(r'^contract/([0-9]+)/$',showcontract),
    url(r'^checkcontract$', checkcontract),
    url(r'^checkcontracts$', checkcontracts),
    url(r'^terminatecon$', terminatecon),
    url(r'^rollbackcontracts$', rollbackcontracts),
    url(r'^querycontracts$', querycontracts),
    url(r'^altercontract$', altercontract),
    url(r'^newfield$', newfield),
    url(r'^newbigparty$', newbigparty),
    url(r'^newparty$', newparty),
    url(r'^newmanager$', newmanager),
    url(r'^newproduct$', newproduct),
    url(r'^product/([0-9]+)/$',showproduct),
    url(r'^products$',queryproducts),
    url(r'^settings$', userctl),
    url(r'^queryrepayitems/([0-9]+)/$', queryrepayitems),
    url(r'^outputfile/([0-9]+)/$', outputfile),
    url(r'^deleteuser$', deleteuser),
    url(r'^passwd$', passwd),
    url(r'^log$', getlog),
    url(r'^repayplan$', repayplan),
    url(r'^dayrepay/([0-9]{4}-[0-9]{2}-[0-9]{2})$', dayrepay),
    url(r'^intocnt$', intocnt),
    url(r'^getbigparties/(.+)$', getbigparties),
    url(r'^getparties/(.+)$', getparties),
    url(r'^getmanagers/(.+)$', getmanagers),
    url(r'^getpersoncnt/(.+)$', getpersoncnt),
    url(r'^yearintocnt$', yearintocnt),
    url(r'^repaycnt$', repaycnt),
    url(r'^waitrepay$', waitrepay),
    url(r'^lastcheck$', lastcheck),
    url(r'^repayitem/([0-9]+)$', getrepayitem),
    url(r'^construct$', getconstruct),
    url(r'^ajust/([0-9]+)/$', ajust),
    #url(r'^product/([0-9]+)$', getproduct),
]
