import getTeamsMsg
import s2dingding
import time
from apscheduler.schedulers.blocking import BlockingScheduler
import datetime
from chinese_calendar import is_workday
scheduler = BlockingScheduler()
def trans_msg():
    json_msg = getTeamsMsg.getchatMsg()

    for chat in json_msg.keys():

        msg_list = json_msg[chat]
        if len(msg_list) != 0:
            for msg in reversed(msg_list):
                send_msg = "%s：\n%s"%(chat,str(msg).strip('{').strip('}'))
                s2dingding.s2dd(send_msg)


def running_plan():
    ismsg = scheduler.get_job(job_id='msg')
    if ismsg:
        scheduler.remove_job(job_id='msg')

    today = datetime.date.today()
    workday = is_workday(today)
    if workday:
        scheduler.add_job(trans_msg, 'cron', hour='0-8,18-23', second='0,10,20,30,40,50', id='msg', max_instances=3)
    else:
        scheduler.add_job(trans_msg, 'cron', hour='0-23', second='0,10,20,30,40,50', id='msg', max_instances=3)

scheduler.add_job(running_plan, 'cron', hour='0', id='iswork')
running_plan()
scheduler.start()