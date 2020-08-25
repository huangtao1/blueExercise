from celery import task
import datetime
import time
from .models import ScriptExecuteRecord


@task
def async_status(client, data, service_id):
    num = 0
    tag = True
    job_id = data["task_id"]
    biz_id = service_id
    kwargs = {"bk_biz_id": biz_id, "job_instance_id": job_id}

    while True:
        job_data = client.job.get_job_instance_status(kwargs)
        if job_data.get('result', False):
            is_finished = job_data['data']['is_finished']
            job_instance = job_data['data']['job_instance']
            status = job_instance['status']
            create_time = job_instance['create_time'][:-6]
            start_time = job_instance['start_time'][:-6]
            if job_instance.get('end_time', ''):
                end_time = job_instance['end_time'][:-6]
            else:
                end_time = datetime.datetime.now()
            data["create_time"] = create_time
            data["execute_time"] = start_time
            data["result"] = is_finished
            data["end_time"] = end_time
            data["state"] = status
            if int(status) == 2:
                time.sleep(5)
            else:
                tag = True
                break
        else:
            num += 1
            if num > 5:
                tag = False
                break
            time.sleep(5)
    if tag:
        # 写入数据
        ScriptExecuteRecord.objects.create(**data)
