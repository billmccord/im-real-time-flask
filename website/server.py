from socketio.sgunicorn import GeventSocketIOWorker


class CustomGeventSocketIOWorker(GeventSocketIOWorker):
    transports = ['xhr-polling']
