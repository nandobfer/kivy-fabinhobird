import socketio


class Socket():
    def __init__(self):
        print('connecting...')
        self.sio = socketio.Client()

        @self.sio.on('connect')
        def connect():
            connected = True
            print('connection established')

        @self.sio.on('connected')
        def connected(data):
            print('server sid: ', data)

        @self.sio.on('disconnect')
        def disconnect():
            print('disconnecting from the server...')

        @self.sio.on('new_connection')
        def onNewConnection(sid):
            print(f'new connection from: {sid}')

        self.sio.connect('http://192.168.18.9:5000')
        # self.sio.wait()

    def disconnect(self):
        self.sio.disconnect()
