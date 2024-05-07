import zmq
import time

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5557")

# Managing separate states for each timer type
timer_states = {
    'pomodoro': False,
    'short_break': False,
    'long_break': False
}

def main():
    while True:
        message = socket.recv_json()
        action = message['action']
        timer_type = message.get('timer_type', 'pomodoro')  # Default to 'pomodoro' if not specified

        if action == 'start':
            # Check if any timer is already running
            if any(timer_states.values()):
                socket.send_json({'status': 'error', 'message': 'Another timer is already running'})
            else:
                timer_states[timer_type] = True
                duration = message['duration']
                # Start the timer logic (example)
                start_time = time.time()
                elapsed_time = 0
                while elapsed_time < duration:
                    time.sleep(1)
                    elapsed_time = time.time() - start_time
                timer_states[timer_type] = False
                socket.send_json({'status': 'success', 'message': 'Timer completed'})

        elif action == 'stop':
            if timer_states[timer_type]:
                timer_states[timer_type] = False
                socket.send_json({'status': 'success', 'message': 'Timer stopped'})
            else:
                socket.send_json({'status': 'error', 'message': 'Timer not running'})

        # Add more actions like 'pause', 'resume' etc., handling them similarly

if __name__ == "__main__":
    main()
