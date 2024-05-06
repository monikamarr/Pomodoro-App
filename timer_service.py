import zmq
import time

def main():
    context = zmq.Context()
    socket = context.socket(zmq.REP)  # Consider using ROUTER for handling multiple clients
    socket.bind("tcp://*:5555")

    timers = {}  # Dictionary to manage multiple timers

    while True:
        message = socket.recv_json()
        client_id = message.get('client_id', 'default_client')
        action = message['action']

        if action == 'start':
            duration = message.get('duration', 1500)  # Default 25 minutes
            timers[client_id] = {
                'start_time': time.perf_counter(),
                'duration': duration,
                'running': True
            }
            socket.send_json({'status': 'Timer started'})
        elif action == 'check':
            if client_id in timers and timers[client_id]['running']:
                elapsed = time.perf_counter() - timers[client_id]['start_time']
                running = elapsed < timers[client_id]['duration']
                elapsed = min(elapsed, timers[client_id]['duration'])
                socket.send_json({'elapsed': elapsed, 'running': running})
            else:
                socket.send_json({'elapsed': 0, 'running': False})
        elif action == 'stop':
            if client_id in timers:
                timers[client_id]['running'] = False
            socket.send_json({'status': 'Timer stopped'})

if __name__ == "__main__":
    main()
