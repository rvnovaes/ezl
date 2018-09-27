from channels.routing import route
from chat.consumers import ws_message, ws_connect, ws_disconnect

channel_routing = [
    route('websocket.connect', ws_connect, path=r"^/ws/(?P<label>)"),
    route('websocket.receive', ws_message, path=r"^/ws/(?P<label>)"),
    route('WebSocket.disconnect', ws_disconnect, path=r"^/ws/(?P<label>)")
]
