import json
from channels.handler import AsgiHandler
from channels import Group
from channels.sessions import channel_session
from channels.auth import channel_session_user, channel_session_user_from_http
from chat.models import Chat, Message

@channel_session_user_from_http
def ws_connect(message):
    message.reply_channel.send({'accept': True})
    Group("chat").add(message.reply_channel)

@channel_session_user
def ws_message(message):
    data = json.loads(message['text'])
    chat, created = Chat.objects.get_or_create(pk=int(data.get('chat')))
    chat.messages.create(create_user=message.user, message=data.get('text'))
    data['user'] = message.user.username    
    Group('chat').send({
            'text': json.dumps(data),
            })

@channel_session_user
def ws_disconnect(message):
    Group('chat').discard(message.reply_channel)
