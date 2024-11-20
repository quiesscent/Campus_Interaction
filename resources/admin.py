from django.contrib import admin

# Register your models here.
from .models import Files, Links
admin.site.register(Files)
admin.site.register(Links)