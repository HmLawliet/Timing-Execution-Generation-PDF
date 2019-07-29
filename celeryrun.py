import json
from celery import Celery
from celerytask_querysql import CommandHandler
from celery.task.schedules import crontab 
from celery.decorators import periodic_task
from celeryconfig import Config_Celery,Config_Crontab
from celerytask_charts import Generate_Report

app = Celery()
app.config_from_object(Config_Celery)

# 定时服务
@app.task
@periodic_task(run_every=crontab(minute=Config_Crontab.minute, hour=Config_Crontab.hour, day_of_month=Config_Crontab.day_of_month))
def timing_server():
    c = CommandHandler()
    # c.count_byday()


@app.task
@periodic_task(run_every=crontab(minute=Config_Crontab.minute, hour=Config_Crontab.hour, day_of_month=Config_Crontab.day_of_month))
def generate_pdf_1_server():
    c = CommandHandler()
    r = Generate_Report('日度报表','2019.07.27-07.28')
    g_data = c.reorganize_count_byday(2)
    r.Template_1(g_data,'按照天来统计')
    g_data = c.reorganize_count_byperiod(2)
    r.Template_1(g_data, isdraw = True)


if __name__ == "__main__":
    generate_pdf_1_server()


