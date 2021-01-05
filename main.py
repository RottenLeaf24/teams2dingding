# coding=gbk
import getTeamsMsg
import s2dingding
import time
from apscheduler.schedulers.blocking import BlockingScheduler
def trans_msg():
    json_msg = getTeamsMsg.getchatMsg()

    for chat in json_msg.keys():

        msg_list = json_msg[chat]
        if len(msg_list) != 0:
            for msg in reversed(msg_list):
                send_msg = "%s：\n%s"%(chat,str(msg).strip('{').strip('}'))
                s2dingding.s2dd(send_msg)
while True:
    trans_msg()
    time.sleep(10)
