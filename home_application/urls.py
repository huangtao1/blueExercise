# -*- coding: utf-8 -*-

from django.conf.urls import url

from . import views

urlpatterns = (
    url(r'^$', views.home),
    url(r'^dev-guide/$', views.dev_guide),
    url(r'^contact/$', views.contact),
    url(r'^task-record/$', views.task_record),
    url(r'^task-exec/$', views.task_execute),
    url(r'^task-service-host/$', views.get_hosts),
    url(r'^task-exec-start/$', views.exec_script),
    url(r'^task-record-history/$', views.get_task_records),
    url(r'^query-record-history/$', views.query_task_records)
)
