# -*- coding: utf-8 -*-
from django.shortcuts import render, HttpResponse
from .models import ScriptTemplates, ScriptExecuteRecord
from blueking.component.shortcuts import get_client_by_request
from blueapps.account.models import User
import config
import json
import base64
from datetime import datetime
from .celery_tasks import async_status


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
    # 业务数据
    services = result['data']['info']
    # 用户
    users = User.objects.all()
    # 执行记录
    task_records = ScriptExecuteRecord.objects.all()
    tasks = ScriptTemplates.objects.all()
    data = {'services': services, 'users': users, 'task_records': task_records, 'tasks': tasks}
    return render(request, 'home_application/task_record.html', data)


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
        server_infos = {
            "items": [
                {"index": index + 1, "ip": host_info['host']['bk_host_innerip'], "os": host_info['host']['bk_os_name']}
                for index, host_info in enumerate(result['data']['info'])]}
        return HttpResponse(json.dumps(server_infos), content_type='application/json')


def exec_script(request):
    if request.method == "POST":
        # 获取业务id
        service_id = int(request.POST.get('service_id'))
        # 获取脚本id
        script_id = request.POST.get('script_id')
        script = ScriptTemplates.objects.get(id=script_id)
        script_name = script.name
        # 加密content
        script_content = str(base64.b64encode(script.content.encode('utf-8')), 'utf-8')
        # 获取ip
        ip_list = request.POST.getlist('ip_list')
        # 传值给作业平台
        client = get_client_by_request(request)
        kwargs = {"bk_app_code": config.APP_CODE,
                  "bk_app_secret": config.SECRET_KEY,
                  "bk_username": request.user.username,
                  "bk_biz_id": service_id,
                  "script_content": script_content,
                  "account": "root",
                  "ip_list": [
                      {"bk_cloud_id": 0, "ip": ip} for ip in ip_list]}
        task_result = client.job.fast_execute_script(kwargs)
        print(task_result)
        # 数据写入任务执行记录表
        # 业务名称
        service_args = {
            "bk_app_code": config.APP_CODE,
            "bk_app_secret": config.SECRET_KEY,
            "fields": [
                "bk_biz_name"
            ],
            "condition": {
                "bk_biz_id": service_id
            },
            "page": {
                "start": 0,
                "limit": 10,
                "sort": ""
            }
        }
        # 业务名称
        service_name = client.cc.search_business(service_args)['data']['info'][0]['bk_biz_name']
        # 启动用户名
        username = request.user.username
        # task_id
        task_id = task_result['data']['job_instance_id']
        # 执行开始时间
        execute_time = datetime.now()
        # machine_num
        machine_num = len(ip_list)
        # machine_ip
        machine_ip = json.dumps(ip_list)
        # params
        params = ""
        new_record_info = {"service_name": service_name, "username": username, "task_id": task_id,
                           "execute_time": execute_time,
                           "machine_num": machine_num,
                           "machine_ip": machine_ip, "params": params, "script_id": script_id,
                           "script_name": script_name}
        if task_result.get('result', False):
            async_status(client=client, data=new_record_info, service_id=service_id)

        return HttpResponse(json.dumps({"message": task_result['message']}), content_type='application/json')


class TimeEncoder(json.JSONEncoder):
    """
    序列化orm中的时间列
    """

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return json.JSONEncoder.default(self, obj)


def get_task_records(request):
    # 执行记录
    task_records = ScriptExecuteRecord.objects.all()
    record_info = {
        "items": [{"service_name": record.service_name, "username": record.username, "script_name": record.script_name,
                   "execute_time": record.execute_time,
                   "machine_num": record.machine_num,
                   "machine_ip": record.machine_ip, "state": record.state, "params": record.params,
                   "result": record.result} for record in task_records]}
    return HttpResponse(json.dumps(record_info, cls=TimeEncoder), content_type='application/json')


def query_task_records(request):
    # 执行记录
    biz_name = request.POST.get("biz_name")
    username = request.POST.get("username")
    script_name = request.POST.get("task_name")
    starttime, endtime = request.POST.get("time").split("-")
    starttime = starttime.strip().replace("/", "-") + '00:00:00'
    endtime = endtime.strip().replace("/", "-") + '23:59:59'
    start_time = datetime.strftime(starttime, '%Y-%m-%d %H:%M:%S')
    end_time = datetime.strftime(endtime, '%Y-%m-%d %H:%M:%S')
    task_records = ScriptExecuteRecord.objects.all()
    #task_records = task_records.filter(service_name=biz_name).filter(username=username).filter(script_name=script_name)
    #task_records = task_records.filter(create_time__range=(start_time, end_time))
    record_info = {
        "items": [{"service_name": record.service_name, "username": record.username, "script_name": record.script_name,
                   "execute_time": record.execute_time,
                   "machine_num": record.machine_num,
                   "machine_ip": record.machine_ip, "state": record.state, "params": record.params,
                   "result": record.result} for record in task_records]}
    return HttpResponse(json.dumps(record_info, cls=TimeEncoder), content_type='application/json')
