import zmq
import json

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5558")

tasks = []

def handle_request(message):
    action = message['action']
    if action == 'add':
        tasks.append({'description': message['description'], 'completed': False})
        return {'status': 'Task added'}
    elif action == 'edit':
        index = message['index']
        tasks[index]['description'] = message['description']
        return {'status': 'Task edited'}
    elif action == 'delete':
        index = message['index']
        del tasks[index]
        return {'status': 'Task deleted'}
    elif action == 'toggle_complete':
        index = message['index']
        tasks[index]['completed'] = not tasks[index]['completed']
        return {'status': 'Completion toggled'}
    elif action == 'get_all':
        return {'tasks': tasks}

def main():
    while True:
        message = socket.recv_json()
        response = handle_request(message)
        socket.send_json(response)

if __name__ == "__main__":
    main()
