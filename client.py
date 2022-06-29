import socketio


class Socket():
    def __init__(self):
        print('connecting...')
        self.sio = socketio.Client()
        self.sid = None
        self.player = None
        self.player2 = None
        self.start = False

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

        @self.sio.on('get-server-data')
        def onGetServerData(data):
            if self.player2:
                self.player2.skin = data['skin']
                print(self.player2.skin)

        @self.sio.on('get-server-ready')
        def onGetServerReady():
            if self.player2:
                self.player2.ready = True

        @self.sio.on('server-start-game')
        def onServerStartGame():
            self.start = True

        @self.sio.on('tap')
        def onTap():
            self.player2.tapped = True

        @self.sio.on('pos')
        def onPos(data):
            self.player2.pos = data['pos']

        self.sio.connect('http://44.205.67.5:5001')
        # self.sio.wait()

    def disconnect(self):
        self.sio.disconnect()

    def SendMultiplayerData(self):
        data = {
            'skin': self.player.skin
        }
        self.sio.emit('get-client-data', data)

    def sendMultiplayerReady(self):
        data = {
            'ready': self.player.ready
        }
        self.sio.emit('get-client-ready', data)

    def sendGameTap(self):
        self.sio.emit('tap')

    def sendPos(self):
        data = {
            'pos': self.player.pos
        }
        self.sio.emit('pos', data)
        return self.player2.pos


class Player():
    def __init__(self, data):
        self.sid = data['sid']
        self.player = data['player']
        self.skin = None
        self.ready = False
        self.tapped = False
        self.pos = None
