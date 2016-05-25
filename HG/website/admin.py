from django.contrib import admin

# Register your models here.
from website.models import *
 
admin.site.register(product)
admin.site.register(field)
admin.site.register(bigparty)
admin.site.register(party)
admin.site.register(manager)
admin.site.register(contract)
admin.site.register(repayitem)
