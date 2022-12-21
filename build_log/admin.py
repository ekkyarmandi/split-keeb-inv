from django.contrib import admin

from .models import *

admin.site.register(BuildLog)
admin.site.register(ItemOut)
admin.site.register(SoldOut)