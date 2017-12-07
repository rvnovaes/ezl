import json
from channels.handler import AsgiHandler
from channels import Group


def ws_connect(message):
    message.reply_channel.send({'accept': True})
    Group("chat").add(message.reply_channel)


def ws_message(message):
    # import pdb; pdb.set_trace()
    Group('chat').send({
        'text': json.dumps(json.loads(message['text']))
    })


def ws_disconnect(message):
    Group('chat').discard(message.reply_channel)
