import zmq
import time

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5557")

# Default durations for breaks in seconds
break_durations = {
    'short_break': 300,  # 5 minutes
    'long_break': 900  # 15 minutes
}


def main():
    while True:
        message = socket.recv_json()
        action = message['action']

        if action == 'get_duration':
            # Return the duration of the specified break type
            break_type = message['break_type']
            duration = break_durations.get(break_type, 300)  # Default to 5 minutes if not found
            socket.send_json({'duration': duration})

        elif action == 'set_duration':
            # Set the duration of a specific break type
            break_type = message['break_type']
            duration = message['duration']
            break_durations[break_type] = duration
            socket.send_json({'status': 'Duration Updated'})

        elif action == 'start_break':
            # Start the break countdown
            break_type = message['break_type']
            duration = break_durations[break_type]
            start_time = time.time()
            while duration > 0:
                if time.time() - start_time >= duration:
                    break
                time.sleep(1)  # Check every second
            socket.send_json({'status': 'Break Complete', 'break_type': break_type})


if __name__ == "__main__":
    main()
