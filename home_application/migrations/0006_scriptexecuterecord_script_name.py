# Generated by Django 2.2.6 on 2020-08-28 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home_application', '0005_scriptexecuterecord_script_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='scriptexecuterecord',
            name='script_name',
            field=models.CharField(default='abc', max_length=100, verbose_name='执行脚本的名称'),
            preserve_default=False,
        ),
    ]