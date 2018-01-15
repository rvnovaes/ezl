from channels.routing import route
from chat.consumers import ws_message, ws_connect, ws_disconnect


channel_routing = [
    route('websocket.connect', ws_connect),
    route('websocket.receive', ws_message),
    ]
