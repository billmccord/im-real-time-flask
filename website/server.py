from socketio.sgunicorn import GeventSocketIOWorker


class CustomGeventSocketIOWorker(GeventSocketIOWorker):
    policy_listener = "0.0.0.0:843"
