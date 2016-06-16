from django.contrib import admin

# Register your models here.
from website.models import *
class ContractAdmin(admin.ModelAdmin):
    list_display=("number","client_name","client_idcard")
    search_fields=("number","client_name")
class ProductAdmin(admin.ModelAdmin):
    list_display=("name","rate")
    search_fields=["name"]
class ManagerAdmin(admin.ModelAdmin):
    list_display=("number","name")
    search_fields=("number","name")
    
class RepayitemAdmin(admin.ModelAdmin):
    list_display=("id","repaydate","repaymoney")
    search_fields=("id","repaydate")
    
class FieldAdmin(admin.ModelAdmin):
    list_display=("name","address","tel")
   
class BigpartyAdmin(admin.ModelAdmin):
    list_display=["name"]

class PartyAdmin(admin.ModelAdmin):
    list_display=["name"]

admin.site.register(product,ProductAdmin)
admin.site.register(field,FieldAdmin)
admin.site.register(bigparty,BigpartyAdmin)
admin.site.register(party,PartyAdmin)
admin.site.register(manager,ManagerAdmin)
admin.site.register(contract,ContractAdmin)
admin.site.register(repayitem,RepayitemAdmin)
