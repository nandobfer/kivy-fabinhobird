import socketio


class Socket():
    def __init__(self):
        print('connecting...')
        self.sio = socketio.Client()
        self.sid = None
        self.player = None
        self.player2 = None
        self.skin = None

        @self.sio.on('connect')
        def connect():
            connected = True
            print('connection established')

        @self.sio.on('player')
        def newPlayer(data):
            self.sid = data['sid']
            self.player = Player(data)

        @self.sio.on('connected')
        def connected(sid):
            print('server sid: ', sid)

        @self.sio.on('disconnect')
        def disconnect():
            print('disconnecting from the server...')

        @self.sio.on('new_connection')
        def onNewConnection(sid):
            print(f'new connection from: {sid}')

        @self.sio.on('2-player-join')
        def on2PlayerJoin(data):
            self.player2 = Player(data)

        @self.sio.on('2-player-leave')
        def on2PlayerLeave(data):
            if data['sid'] == self.player2.sid:
                self.player2 = None

        @self.sio.on('send-multiplayer-data')
        def onSendMultiplayerData():
            data = {
                'skin': self.skin
            }
            self.sio.emit('get-client-data', data)

        self.sio.connect('http://44.205.67.5:5001')
        # self.sio.wait()

    def disconnect(self):
        self.sio.disconnect()


class Player():
    def __init__(self, data):
        self.sid = data['sid']
        self.player = data['player']
