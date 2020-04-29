# -*- coding: utf-8 -*-
from django.shortcuts import render, HttpResponse
from .models import ScriptTemplates
from blueking.component.shortcuts import get_client_by_request
import config
import json


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
    client = get_client_by_request(request)
    kwargs = {
        "bk_app_code": config.APP_CODE,
        "bk_app_secret": config.SECRET_KEY,
        "fields": [
            "bk_biz_id",
            "bk_biz_name"
        ],
        "page": {
            "start": 0,
            "limit": 10,
            "sort": ""
        }
    }
    result = client.cc.search_business(kwargs)
    services = result['data']['info']
    tasks = ScriptTemplates.objects.all()
    data = {"tasks": tasks, "services": services}
    return render(request, 'home_application/task_execute.html', data)


def get_hosts(request):
    if request.method == "POST":
        # 获取业务id
        service_id = request.POST.get('service_id')
        # 查询业务对应机器
        client = get_client_by_request(request)
        kwargs = {"bk_app_code": config.APP_CODE,
                  "bk_app_secret": config.SECRET_KEY,
                  "bk_biz_id": service_id,
                  "condition": [
                      {"bk_obj_id": "host",
                       "fields": ["bk_host_innerip", "bk_os_name"]
                       }
                  ],
                  "page": {
                      "start": 0,
                      "limit": 10,
                      "sort": "bk_host_id"}
                  }
        result = client.cc.search_host(kwargs)
        print(result)
        server_infos = {"catalogues": {
            "index": "#",
            "name": "名称",
            "position": "位置",
            "date": "日期",
            "type": "类型"
        },
            "items": [
                {"index": index + 1, "ip": host_info['host']['bk_host_innerip'], "os": host_info['host']['bk_os_name']}
                for index, host_info in
                enumerate(result['data']['info'])]}
        return HttpResponse(json.dumps(server_infos), content_type='application/json')
