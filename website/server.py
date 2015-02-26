from socketio.sgunicorn import GeventSocketIOWorker


class CustomGeventSocketIOWorker(GeventSocketIOWorker):
    transports = ['websocket', 'xhr-polling']
