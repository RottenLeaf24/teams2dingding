import requests
import getToken
import json,yaml,os
import logging
logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
config = yaml.full_load(open('config.yaml'))['teamschat']
def get_chat_id(chatname):
    '''
    Get the chat id by chatname.
    :param chatname:
    :return:
    '''
    token = getToken.gene_token()
    url = 'https://graph.microsoft.com/beta/me/chats'
    headers = {'Authorization': 'Bearer %s' % token.strip()}
    res = requests.get(url,headers=headers)
    if res.status_code == 200:
        print(res.json())
    else:
        print(res.status_code,res.json())
def _getUserId(userPrincipalName):
    '''
    Get user id by userPrincipalName
    :return: a dict contain user name and user id.
    '''
    token = getToken.gene_token()
    graph_data = requests.get(  # Use token to call downstream service
        'https://graph.microsoft.com/beta/users/%s' %userPrincipalName,
        headers={'Authorization': 'Bearer ' + token},
        ).json()

    return graph_data['id']
def _selectChat(chats):
    '''
    select which chats need to get info
    :return: a dictionary contain chat/user name and id
    '''
    
    selectUser = config['oneonone']
    selectChat = config['group']
    chatinfo = {}
    oneONone_list = []
    for chat in chats:
        if chat['topic'] in selectChat:
            chatinfo[chat['topic']] = {"id":chat['id']}
            chatinfo[chat['topic']]['etag'] = None
        elif chat['chatType'] == 'oneOnOne':
            oneONone_list.append(chat)
    for user in selectUser:
        userid = _getUserId(user)
        for chat_one in oneONone_list:
            if userid in chat_one['id']:
                chatinfo[user] = {"id":chat_one['id']}
                chatinfo[user]['etag'] = None
    with open('chatinfo.json','w') as f:
        f.write(json.dumps(chatinfo,indent=2))


def getchatinfo():
    '''
    Get the chat information
    :return: a dict contain chat name and chat id.
    '''
    token = getToken.gene_token()
    res = requests.get(  # Use token to call downstream service
        'https://graph.microsoft.com/beta/me/chats',
        headers={'Authorization': 'Bearer ' + token},
        )
    graph_data = res.json()
    _selectChat(graph_data['value'])
    return res.status_code

def getchatMsg():
    if not os.path.exists('chatinfo.json'):
        getchatinfo()
    with open('chatinfo.json','r') as f:
        chatinfo = json.loads(f.read())

    msg_data = {}
    token = getToken.gene_token()

    for chatname in chatinfo.keys():
        chatid = chatinfo[chatname]['id']
        lastmsg_time = chatinfo[chatname]['etag']
        try:
            res = requests.get(  # Use token to call downstream service
                'https://graph.microsoft.com/beta/me/chats/%s/messages' %chatid,
                headers={'Authorization': 'Bearer ' + token},
            )
            graph_data = res.json()

        except Exception as e:
            response_msg = "Request error ,error message is :%s" %e
            logging.warning(response_msg)
        else:

            msg_list = []
            refresh_lastmsg_time = lastmsg_time

            # msg_records = graph_data['value']
            if res.status_code == 200:
                msg_records = graph_data['value']
                for index, single_msg in enumerate(msg_records):

                    msg_time = single_msg['etag']
                    if msg_time == lastmsg_time:
                        break
                    user = single_msg['from']['user']['displayName']
                    msg_content = single_msg['body']['content']
                    msg_list.append({user: msg_content})
                    if index == 0:
                        refresh_lastmsg_time = single_msg['etag']
                if len(msg_list) != 0:
                    print(msg_list)
                    logging.info('请求成功，【%s】有新消息产生。' % chatname)
                else:
                    logging.info('请求成功，【%s】无消息。' % chatname)
            else:
                error_response = "请求失败，错误信息：%s" %graph_data
                logging.warning(error_response)

            msg_data[chatname] = msg_list
            chatinfo[chatname]['etag'] = refresh_lastmsg_time
    with open('chatinfo.json','w') as f:
        f.write(json.dumps(chatinfo))

    return msg_data



