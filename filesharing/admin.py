from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from filesharing.models import *

admin.site.register(Directory, MPTTModelAdmin)
admin.site.register(File)
admin.site.register(User)