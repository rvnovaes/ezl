import json
from json.decoder import JSONDecodeError
from channels.handler import AsgiHandler
from channels import Group
from channels.sessions import channel_session
from channels.auth import channel_session_user, channel_session_user_from_http
from chat.models import Chat, Message
from urllib.parse import parse_qs


@channel_session_user_from_http
def ws_connect(message):
    message.reply_channel.send({'accept': True})
    params = parse_qs(message.content['query_string'])
    print('aaaaaaaaaaaa')
    print(params)
    print(params[b'label'])
    if b'label' in params:
        print(params[b'label'])
        group = params[b'label'][0].decode('utf-8')
        Group(group).add(message.reply_channel)
    else:
        message.reply_channel.send({"close": True})


@channel_session_user
def ws_message(message):
    try:
        data = json.loads(message['text'])
        chat, created = Chat.objects.get_or_create(pk=int(data.get('chat')))
        chat.messages.create(create_user=message.user, message=data.get('text'))
        data['user'] = message.user.username
        Group(data.get('label')).send({
                'text': json.dumps(data),
                })
    except JSONDecodeError:
        Group('chat').send({
            'text': message['text'],
        })


@channel_session_user
def ws_disconnect(message):
    Group('chat').discard(message.reply_channel)
