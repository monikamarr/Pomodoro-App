import zmq


def main():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5556")

    # Default settings
    settings = {'pomodoro': 1500, 'short_break': 300, 'long_break': 900}

    while True:
        # Receive a request
        message = socket.recv_json()
        action = message['action']

        if action == 'get_settings':
            # Send the current settings
            try:
                socket.send_json({'status': 'success', 'settings': settings})
            except Exception as e:
                socket.send_json({'status': 'error', 'message': f"Failed to process settings: {str(e)}"})

        elif action == 'update_settings':
            # Update the settings with new durations provided by the client
            new_settings = message['settings']
            for mode, duration in new_settings.items():
                settings[mode] = duration
            socket.send_json({'status': 'Settings updated'})


if __name__ == "__main__":
    main()
