import zmq
import time


def main():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")  # Binding to port 5555 for timer service

    running = False
    paused = False
    start_time = 0
    remaining_time = 0

    while True:
        message = socket.recv_json()
        action = message['action']

        if action == 'start':
            if not running:
                duration = message['duration']
                running = True
                paused = False
                start_time = time.time()
                remaining_time = duration
                response = {'status': 'success', 'message': 'Timer started'}
            else:
                response = {'status': 'error', 'message': 'Timer already running'}

        elif action == 'pause':
            if running and not paused:
                paused = True
                response = {'status': 'success', 'message': 'Timer paused'}
            else:
                response = {'status': 'error', 'message': 'Timer not running or already paused'}

        elif action == 'resume':
            if running and paused:
                paused = False
                elapsed = time.time() - start_time
                remaining_time -= int(elapsed)
                start_time = time.time()
                response = {'status': 'success', 'message': 'Timer resumed'}
            else:
                response = {'status': 'error', 'message': 'Timer not paused or not running'}

        elif action == 'check':
            if running:
                elapsed = time.time() - start_time
                remaining_time = max(0, remaining_time - int(elapsed))
                response = {'running': True, 'elapsed': remaining_time, 'status': 'success'}
            else:
                response = {'running': False, 'paused': paused, 'status': 'success'}

        elif action == 'reset':
            if running:
                running = False
                paused = False
                start_time = 0
                remaining_time = 0
                response = {'status': 'success', 'message': 'Timer reset'}
            else:
                response = {'status': 'error', 'message': 'Timer was not running'}

        # Send response after processing the action
        socket.send_json(response)


if __name__ == "__main__":
    main()
