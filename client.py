import socketio


class Socket():
    def __init__(self):
        print('connecting...')
        self.sio = socketio.Client()
        self.player2 = None

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
            
        @self.sio.on('2-player-join')
        def on2PlayerJoin(data):
            self.player2 = Player2(data['sid'])

        self.sio.connect('http://44.206.122.252:5001')
        # self.sio.wait()

    def disconnect(self):
        self.sio.disconnect()
        
class Player2():
    def __init__(self, sid):
        self.sid = sid
        
