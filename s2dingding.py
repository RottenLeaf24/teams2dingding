import requests

def s2dd(msg):
    headers={"Content-Type": "application/json"}
    url = 'https://oapi.dingtalk.com/robot/send?access_token=YourRobotAccessToken'
    data = {"msgtype": "text","text": {"content": msg}}

    res = requests.post(url,headers=headers,json=data)
    if res.status_code == 200:
        return "发送成功！"
    else:
        return "发送失败，错误信息为: %s" %res.text

