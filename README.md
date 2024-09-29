<iframe src="https://giphy.com/embed/tHd9hYitHFY4bnh9RN" width="390" height="480" style="" frameBorder="0" class="giphy-embed" allowFullScreen></iframe><p><a href="https://giphy.com/gifs/tHd9hYitHFY4bnh9RN">via GIPHY</a></p>
# App Overview
The Pomodoro app is designed to boost productivity by managing work and rest periods through a customizable timer. The app is built using a microservices architecture, where each service is responsible for a specific aspect of the app's functionality. 
Below is a brief overview of the main microservices:

## Microservice B: Timer Service
The Timer Service manages the core Pomodoro timer functionality. It allows users to start, pause, and resume the timer, ensuring accurate tracking of work and break periods. This service is essential for maintaining the reliability and usability of the timing mechanism.

## Microservice C: Task Management Service
The Task Management Service handles the creation, listing, and completion of tasks. Users can view their tasks, track their progress by marking tasks as completed, and plan their work sessions accordingly. This service ensures that the task-related functionalities are intuitive and persistent across user sessions.

## Microservice D: Settings Service
The Settings Service allows users to customize the duration of their Pomodoro sessions and breaks. Users can tailor the timer to fit their personal productivity preferences by adjusting these durations. The service also ensures that these settings are applied consistently across all future sessions.

### Communication Between Microservices
The microservices communicate asynchronously using ZeroMQ, which allows for real-time updates and seamless user interaction without blocking the user interface.

## How to Run the Application

To get the Pomodoro application up and running, follow these steps:

### Prerequisites

Make sure you have the following installed:

- **Python 3.x**: The application is built using Python, so you need Python installed on your machine.
- **ZeroMQ**: This is required for communication between the microservices.

You can install the necessary Python packages using `pip`:

```bash
pip install pyzmq
```

### Steps to Run

1. **Clone the Repository:**

   First, clone this repository to your local machine:

   ```bash
   git clone https://github.com/monikamarr/Pomodoro-App.git
   cd pomodoro-app


2. **Run Each Microservice:**

The application consists of three microservices, each of which needs to be run in separate terminal.

**Timer Service (Microservice B):**

Navigate to the directory containing the Timer Service and run the following command:

```bash
python timer_service.py
```
**Task Management Service (Microservice C):**

In another terminal window, navigate to the directory containing the Task Management Service and run:

```bash
python task_service.py
```
**Settings Service (Microservice D):**

In another terminal window, navigate to the directory containing the Settings Service and run:

```bash
python settings_service.py
```

### Interact with the Application:

With all microservices running, you can now interact with the Pomodoro app. parately.

Stopping the Application
To stop the application, you can simply terminate the running Python processes in each terminal window.
