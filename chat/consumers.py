import json
from json.decoder import JSONDecodeError
from channels.handler import AsgiHandler
from channels import Group
from channels.sessions import channel_session
from channels.auth import channel_session_user, channel_session_user_from_http
from chat.models import Chat, Message, UserByChat, UnreadMessage
from urllib.parse import parse_qs
from django.utils import timezone
from django.db.models import Q


@channel_session_user_from_http
def ws_connect(message):
    message.reply_channel.send({'accept': True})
    params = parse_qs(message.content['query_string'])
    if b'label' in params:
        group = params[b'label'][0].decode('utf-8')
        Group(group).add(message.reply_channel)
    else:
        message.reply_channel.send({"close": True})

@channel_session_user
def ws_message(message):
    try:
        data = json.loads(message['text'])
        chat, created = Chat.objects.get_or_create(pk=int(data.get('chat')))
        chat_message = chat.messages.create(create_user=message.user, message=data.get('text'))
        chat.save()
        for user in UserByChat.objects.filter(~Q(user_by_chat=message.user), chat=chat):
            UnreadMessage.objects.create(create_user=message.user, user_by_message=user,
                                         message=chat_message)
        data['user'] = message.user.username
        data['message_create_date'] = timezone.localtime(timezone.now()).strftime('%Y-%m-%d %H:%M')
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
