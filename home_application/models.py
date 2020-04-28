# -*- coding: utf-8 -*-
from django.db import models


# Create your models here.
class ScriptTemplates(models.Model):
    name = models.CharField(max_length=50, verbose_name="脚本名称")
    content = models.TextField(verbose_name="脚本内容")

    def __repr__(self):
        return "script name:%s" % self.name
