# -*- coding: utf-8 -*-
from django.shortcuts import render
from .models import ScriptTemplates


# 开发框架中通过中间件默认是需要登录态的，如有不需要登录的，可添加装饰器login_exempt
# 装饰器引入 from blueapps.account.decorators import login_exempt
def home(request):
    """
    首页
    """
    return render(request, 'home_application/index_home.html')


def dev_guide(request):
    """
    开发指引
    """
    return render(request, 'home_application/dev_guide.html')


def contact(request):
    """
    联系页
    """
    return render(request, 'home_application/contact.html')


def task_record(request):
    """
    任务记录
    """
    return render(request, 'home_application/task_record.html')


def task_execute(request):
    """
    执行任务
    """
    tasks = ScriptTemplates.objects.all()
    data = {"tasks": tasks}
    return render(request, 'home_application/task_execute.html', data)
