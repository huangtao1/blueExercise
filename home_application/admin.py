# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import ScriptTemplates, ScriptExecuteRecord

# Register your models here.
admin.site.register(ScriptTemplates)
admin.site.register(ScriptExecuteRecord)
