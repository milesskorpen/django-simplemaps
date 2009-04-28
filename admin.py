from django.contrib import admin
from tumblelog.gmaps.models import *

class GAddressAdmin(admin.ModelAdmin):
    list_display = ('name','address','description')
    
class GMapAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name','description')
    
admin.site.register(GAddress, GAddressAdmin)
admin.site.register(GMap,GMapAdmin)
