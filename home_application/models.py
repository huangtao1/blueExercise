# -*- coding: utf-8 -*-
from django.db import models


# Create your models here.
class ScriptTemplates(models.Model):
    name = models.CharField(max_length=50, verbose_name="脚本名称")
    content = models.TextField(verbose_name="脚本内容")

    def __repr__(self):
        return "script name:%s" % self.name


class ScriptExecuteRecord(models.Model):
    service_name = models.CharField(max_length=100, verbose_name="业务名称")
    username = models.CharField(max_length=50, verbose_name="执行用户名")
    task_id = models.CharField(max_length=100, verbose_name="执行任务的id")
    script_id = models.CharField(max_length=100, verbose_name="执行脚本的id")
    create_time = models.DateTimeField(verbose_name="任务下发时间")
    execute_time = models.DateTimeField(verbose_name="开始执行的时间")
    machine_num = models.IntegerField(verbose_name="执行的ip数")
    machine_ip = models.TextField(verbose_name="执行的ip信息")
    state = models.CharField(max_length=20,verbose_name="任务的状态")
    params = models.TextField(verbose_name="执行的参数")
    result = models.TextField(verbose_name="执行详情")
    end_time = models.DateTimeField(verbose_name="执行结束时间")
