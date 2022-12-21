from django.contrib import admin
from .models import *

admin.site.register(Order)
admin.site.register(Sparepart)
admin.site.register(OrderSparepart)