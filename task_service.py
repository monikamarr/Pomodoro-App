import zmq

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5558")

tasks = []

def handle_request(message):
    action = message['action']
    try:
        if action == 'add':
            tasks.append({'description': message['description'], 'completed': False})
            return {'status': 'success', 'message': 'Task added'}
        elif action == 'edit':
            index = int(message['index'])
            if index < len(tasks) and 'description' in message:
                tasks[index]['description'] = message['description']
                return {'status': 'success', 'message': 'Task edited'}
            else:
                return {'status': 'error', 'message': 'Invalid task index'}
        elif action == 'delete':
            index = int(message['index'])
            if index < len(tasks):
                del tasks[index]
                return {'status': 'success', 'message': 'Task deleted'}
            else:
                return {'status': 'error', 'message': 'Invalid task index'}
        elif action == 'toggle_complete':
            index = int(message['index'])
            if index < len(tasks):
                tasks[index]['completed'] = not tasks[index]['completed']
                return {'status': 'success', 'message': 'Completion toggled'}
            else:
                return {'status': 'error', 'message': 'Invalid task index'}
        elif action == 'get_all':
            return {'status': 'success', 'tasks': tasks}
        else:
            return {'status': 'error', 'message': 'Unknown action'}
    except ValueError as e:
        return {'status': 'error', 'message': str(e)}
    except Exception as e:
        return {'status': 'error', 'message': 'Unexpected error occurred'}

def main():
    while True:
        message = socket.recv_json()
        response = handle_request(message)
        socket.send_json(response)

if __name__ == "__main__":
    main()
