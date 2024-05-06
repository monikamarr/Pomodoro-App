import zmq

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5556")

settings = {'pomodoro': 1500, 'short_break': 300, 'long_break': 900}

def main():
    while True:
        message = socket.recv_json()
        action = message['action']

        if action == 'get':
            mode = message.get('mode', 'pomodoro')
            duration = settings.get(mode, 1500)
            socket.send_json({'duration': duration})
        elif action == 'set':
            mode = message['mode']
            duration = message['duration']
            settings[mode] = duration
            socket.send_json({'status': 'saved'})

if __name__ == "__main__":
    main()
