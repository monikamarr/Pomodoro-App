import json
import tkinter as tk
from tkinter import ttk, simpledialog, PhotoImage, messagebox
import time
import zmq
import threading


class PomodoroTimer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.task_frame = None
        self.external_service_button = None
        self.title("Pomodoro App")
        self.geometry("300x500")
        self.configure(bg='#BACD92')
        self.info_text = ""

        # Setup ZeroMQ for communication
        self.context = zmq.Context()

        # communicating with Karen's microservice A
        self.external_service_socket = self.context.socket(zmq.REQ)
        self.external_service_socket.connect("tcp://localhost:5560")

        # communicating with task_service.py
        self.task_socket = self.context.socket(zmq.REQ)
        self.task_socket.connect("tcp://localhost:5558")

        # Setup ZeroMQ for communication with the timer service
        self.timer_socket = self.context.socket(zmq.REQ)
        self.timer_socket.connect("tcp://localhost:5555")

        # Setup ZeroMQ for communication with the settings service
        self.settings_socket = self.context.socket(zmq.REQ)
        self.settings_socket.connect("tcp://localhost:5556")

        # Setup ZeroMQ for communication with the breaks service
        self.breaks_socket = self.context.socket(zmq.REQ)
        self.breaks_socket.connect("tcp://localhost:5557")

        self.durations = self.get_settings()
        self.current_timer = 'pomodoro'
        self.remaining_time = self.durations[self.current_timer]
        self.running = False
        self.paused = False

        self.tasks = []

        self.configure_styles()
        self.setup_ui()

    def configure_styles(self):
        style = ttk.Style(self)
        style.theme_use('clam')  # Ensuring a consistent theme

        # General style for frames and buttons used across the app
        style.configure('TFrame', background='#FCFFE0')
        style.configure('TButton', background='#75A47F', foreground='white', font=('Helvetica', 12))
        # Add hover effects back to the buttons
        style.map('TButton',
                  background=[('active', '#F5DAD2'), ('disabled', 'grey')],
                  foreground=[('active', 'white'), ('disabled', 'grey')])

        # Specific styles for task-related elements
        style.configure('TaskFrame.TFrame', background='#FCFFE0')
        style.configure('TaskButton.TButton', background='#75A47F', font=('Helvetica', 10))
        style.map('TaskButton.TButton',
                  background=[('active', '#67A568'), ('disabled', 'grey')],
                  foreground=[('active', 'white'), ('disabled', 'grey')])

        # Style for labels (consider using a different style name if applied only to specific labels)
        style.configure('TLabel', background='#F5DAD2', foreground='#75A47F', font=('Helvetica', 14))

        # Style for the info button

        style.configure('InfoButton.TButton', background='#75A47F', foreground='white',
                        font=('Arial', 12, 'bold'), width=2)

    # calling on Karen's microservice A
    # def call_external_service(self, type, size):
    #     """Call the external service with a type and size and return the response."""
    #     req = json.dumps({"type": type, "size": size})
    #     self.external_service_socket.send_string(req)
    #     res = self.external_service_socket.recv_string()
    #     return res

    def setup_ui(self):
        # Settings button in the top-right corner
        self.settings_button = ttk.Button(self, text='⚙ Settings', command=self.open_settings)
        self.settings_button.pack(anchor='ne', padx=10, pady=10)

        self.timer_display = ttk.Label(self, text=self.format_time(self.remaining_time), font=('Helvetica', 100))
        self.timer_display.pack(pady=20)

        self.control_button = ttk.Button(self, text="Start", command=self.start_or_pause_timer)
        self.control_button.pack(pady=10)

        self.reset_button = ttk.Button(self, text="Reset", command=self.reset_timer)
        self.reset_button.pack(pady=10)

        mode_frame = ttk.Frame(self)
        mode_frame.pack(pady=10)
        for mode in ['pomodoro', 'short_break', 'long_break']:
            ttk.Button(mode_frame, text=mode.capitalize(),
                       command=lambda m=mode: self.switch_mode(m)).pack(side=tk.LEFT)

        # Task List Frame
        self.task_frame = ttk.Frame(self)
        self.task_frame.pack(fill=tk.BOTH, expand=True)
        self.refresh_tasks()

        # Add Task Entry
        self.task_entry = ttk.Entry(self)
        self.task_entry.pack(pady=10)
        self.add_task_button = ttk.Button(self, text="Add Task", command=self.add_task)
        self.add_task_button.pack()
        self.refresh_tasks()

        # setting info button in lower right corner
        self.info_button = ttk.Button(self, text="ⓘ", style='InfoButton.TButton', command=self.fetch_info)
        # Pack the info button in the lower right corner
        self.info_button.pack(side='right', anchor='se', padx=10, pady=10)

        # Info button setup

       # self.info_button.pack(side='bottom', anchor='se', padx=10, pady=10)

    # popup window
    def fetch_info(self):
        # Assuming request_info method updates a variable self.info_text with the fetched information
        threading.Thread(target=self.request_info, daemon=True).start()
        self.after(100, self.open_info_window)  # Open window after a short delay to ensure data is fetched

    def open_info_window(self):
        info_window = tk.Toplevel(self)
        info_window.title("Information")
        info_window.geometry("400x300")  # Adjust size as needed
        info_window.configure(bg='#F5DAD2')  # Set the background color of the window

        # Create a scrollbar
        scrollbar = ttk.Scrollbar(info_window)
        scrollbar.pack(side='right', fill='y')

        # Create a Text widget with a Scrollbar and custom colors
        text_widget = tk.Text(info_window, wrap='word', yscrollcommand=scrollbar.set,
                              bg='#F5DAD2', fg='#75A47F',  # Light pink background with green text
                              borderwidth=0,
                              highlightthickness=0)  # Remove border to avoid any default background peeking through
        text_widget.pack(expand=True, fill='both', padx=10, pady=10)
        text_widget.config(state='normal')  # Ensure the widget is in a normal state when inserting text
        text_widget.delete('1.0', 'end')  # Clear existing text
        text_widget.insert('end', self.info_text)  # Insert text into the Text widget
        text_widget.config(state='disabled')  # Disable editing of the text widget

        # Configure the scrollbar to scroll the Text widget
        scrollbar.config(command=text_widget.yview)

    def send_request(self, socket, action, data):
        message = {'action': action, **data}
        print(f"Sending: {message}")
        socket.send_json(message)
        response = socket.recv_json()
        print(f"Received: {response}")
        return response

    def request_info(self):
        try:
            context = zmq.Context()
            socket = context.socket(zmq.REQ)
            socket.connect("tcp://localhost:5560")

            requests = [
                {"type": "infoPom", "size": "small"},
                {"type": "infoPom", "size": "medium"},
                {"type": "infoPom", "size": "large"},
                {"type": "aboutPom", "size": "small"},
                {"type": "aboutPom", "size": "medium"},
                {"type": "aboutPom", "size": "large"}
            ]

            combined_response = ""
            for req in requests:
                socket.send_string(json.dumps(req))
                response = socket.recv_string()
                combined_response += response + "\n\n" + "-" * 50 + "\n\n"  # Adding a line after each response

            # Schedule update to `info_text` on the main thread
            self.after(0, lambda: setattr(self, 'info_text', combined_response.strip()))
        except Exception as e:
            print("Error during request:", e)
            self.after(0, lambda: setattr(self, 'info_text', "Error fetching data"))
        finally:
            socket.close()
            context.term()

    # -----------------------------------------------------------
    # TASKS MANAGEMENT
    # -----------------------------------------------------------
    def refresh_tasks(self):
        for widget in self.task_frame.winfo_children():
            widget.destroy()

        for i, task in enumerate(self.tasks):
            self.create_task_widget(i, task)

    def add_task(self):
        task_description = self.task_entry.get()
        if task_description:
            # Send the new task to the task service
            response = self.send_request(self.task_socket, 'add', {'description': task_description})
            if response.get('status') == 'success':
                self.tasks.append({"description": task_description, "completed": False})
                self.task_entry.delete(0, tk.END)
                self.refresh_tasks()

    def delete_task(self, index):
        if 0 <= index < len(self.tasks):
            response = self.send_request(self.task_socket, 'delete', {'index': index})
            if response.get('status') == 'success':
                del self.tasks[index]
                self.refresh_tasks()
            else:
                print("Failed to delete task: ", response.get('message'))
        else:
            print("Invalid task index")

    def toggle_task(self, index, var):
        task = self.tasks[index]
        task['completed'] = var.get()
        # Send the update request to the task service
        self.send_request(self.task_socket, 'update_task',
                          {'description': task['description'], 'completed': task['completed']})
        self.refresh_tasks()

    def create_task_widget(self, index, task):
        task_frame = ttk.Frame(self.task_frame, style='TaskFrame.TFrame')
        task_frame.pack(fill=tk.X, expand=False, pady=0)

        # Create a variable to hold the task completion status
        var = tk.BooleanVar(value=task['completed'])

        # Create the checkbox with the consistent background
        checkbox = tk.Checkbutton(task_frame, text=task['description'], variable=var,
                                  onvalue=True, offvalue=False,
                                  command=lambda: self.toggle_task(index, var),
                                  bg='#F5DAD2', activebackground='#F5DAD2', relief='flat', anchor='w')
        checkbox.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Edit button with consistent background
        edit_button = ttk.Button(task_frame, text="✎ Edit", command=lambda: self.edit_task(index),
                                 style='TaskButton.TButton')
        edit_button.pack(side=tk.RIGHT, anchor='e')

        # Delete button with consistent background
        delete_button = ttk.Button(task_frame, text="✖ Delete", command=lambda: self.confirm_delete_task(index),
                                   style='TaskButton.TButton')
        delete_button.pack(side=tk.RIGHT, anchor='e')

    def edit_task(self, index):
        current_description = self.tasks[index]['description']
        new_description = simpledialog.askstring("Edit Task", "Edit the task description:",
                                                 initialvalue=current_description)
        if new_description and new_description != current_description:
            response = self.send_request(self.task_socket, 'edit', {'index': index, 'description': new_description})
            if response.get('status') == 'success':
                self.tasks[index]['description'] = new_description
                self.refresh_tasks()
            else:
                messagebox.showerror("Error", f"Failed to update task: {response.get('message')}")

    def confirm_delete_task(self, index):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this task? This cannot be undone!"):
            self.delete_task(index)

    # -----------------------------------------------------------
    # SETTINGS SERVICE
    # -----------------------------------------------------------
    def open_settings(self):
        response = self.send_request(self.settings_socket, "get_settings", {})
        if response.get('status') == 'success':
            settings = response['settings']
            settings_window = tk.Toplevel(self)
            settings_window.title("Timer Settings")
            settings_window.geometry("250x150")
            settings_window.configure(background='#F5DAD2')

            row = 0
            entries = {}
            for mode, seconds in settings.items():
                label = ttk.Label(settings_window, text=f"{mode.capitalize()} duration (minutes):")
                label.grid(row=row, column=0, padx=10, pady=5)
                entry = ttk.Entry(settings_window, width=5)
                entry.insert(0, seconds // 60)
                entry.grid(row=row, column=1, padx=5)
                entries[mode] = entry
                row += 1

            def save_settings():
                new_settings = {mode: int(entry.get()) * 60 for mode, entry in entries.items()}
                # Send updated settings back to the server for storage
                update_response = self.send_request(self.settings_socket, "update_settings", {"settings": new_settings})
                if update_response.get('status') == 'Settings updated':
                    for mode in new_settings:
                        self.durations[mode] = new_settings[mode]
                    settings_window.destroy()
                else:
                    messagebox.showerror("Error", update_response.get('message'))

            save_button = ttk.Button(settings_window, text="Save", command=save_settings)
            save_button.grid(row=row, column=0, columnspan=2, pady=10)
        else:
            messagebox.showerror("Error", response.get('message'))

    def get_settings(self):
        # Example of a synchronous call to fetch settings
        response = self.send_request(self.settings_socket, "get_settings", {})
        if response.get('status') == 'success':
            return response['settings']
        else:
            # Handle failure: either return default settings or raise an exception
            return {'pomodoro': 1500, 'short_break': 300, 'long_break': 900}

    # -----------------------------------------------------------
    # TIMER AND BREAKS SERVICES
    # -----------------------------------------------------------

    def start_or_pause_timer(self):
        print("Start or pause timer method called")
        if not self.running:
            print("Timer not running. Starting timer...")
            response = self.send_request(self.timer_socket, 'start', {'duration': self.durations[self.current_timer]})
            if response.get('status') == 'success':
                self.running = True
                self.paused = False
                self.control_button.config(text="Pause")
                self.remaining_time = self.durations[self.current_timer]
                self.timer_display.config(text=self.format_time(self.remaining_time))
                self.update_timer()  # This would now request time updates from the service
            else:
                print("Failed to start timer:", response.get('message'))
                messagebox.showerror("Timer Error", response.get('message'))
        elif self.paused:
            print("Timer paused. Resuming timer...")
            self.resume_timer()
        else:
            print("Timer running. Pausing timer...")
            self.pause_timer()

    def start_timer(self):
        if not self.running:
            response = self.send_request(self.timer_socket, 'start', {'duration': self.durations[self.current_timer]})
            if response.get('status') == 'success':
                self.running = True
                self.paused = False
                self.start_time = time.time()
                self.update_timer()
                self.control_button.config(text="Pause")
                print("Timer started successfully")
            else:
                print(f"Failed to start timer: {response.get('message')}")
                messagebox.showerror("Timer Error", response.get('message'))
        else:
            print("Attempt to start timer while it is already running")

    def pause_timer(self):
        if self.running and not self.paused:
            response = self.send_request(self.timer_socket, 'pause', {})
            if response.get('status') == 'success':
                self.paused = True
                self.control_button.config(text="Resume")

    def resume_timer(self):
        if self.paused:
            response = self.send_request(self.timer_socket, 'resume', {})
            if response.get('status') == 'success':
                self.paused = False
                self.control_button.config(text="Pause")
                self.update_timer()

    def update_timer(self):
        if self.running and not self.paused:
            response = self.send_request(self.timer_socket, 'check', {})
            if response.get('status') == 'success':
                if response['running']:
                    self.remaining_time = response['elapsed']
                    self.timer_display.config(text=self.format_time(self.remaining_time))
                    self.paused = response.get('paused', False)
                    if not self.paused:
                        self.after(1000, self.update_timer)
                else:
                    self.reset_timer()

    def reset_timer(self):
        response = self.send_request(self.timer_socket, 'reset', {})
        if response.get('status') == 'success':
            self.running = False
            self.paused = False
            self.remaining_time = self.durations[self.current_timer]
            self.timer_display.config(text=self.format_time(self.remaining_time))
            self.control_button.config(text="Start")

    def switch_mode(self, mode):
        if self.running:
            self.reset_timer()
        self.current_timer = mode
        self.remaining_time = self.durations[mode]
        self.timer_display.config(text=self.format_time(self.remaining_time))

    def format_time(self, seconds):
        return f"{seconds // 60:02}:{seconds % 60:02}"

    def start_break(self, break_type):
        if self.running:
            messagebox.showinfo("Timer Running", "Stop the main timer before starting a break.")
            return
        response = self.send_request(self.breaks_socket, "start_break", {"break_type": break_type})
        if response.get('status') == 'success':
            messagebox.showinfo("Break Complete", f"{break_type.capitalize()} break is complete!")
        else:
            messagebox.showerror("Error", response.get('message'))

    def get_break_duration(self, break_type):
        response = self.send_request(self.breaks_socket, "get_duration", {"break_type": break_type})
        if response.get('status') == 'success':
            return response['duration']
        else:
            messagebox.showerror("Error",
                                 f"Failed to get duration for {break_type}: {response.get('message', 'No details provided')}")
            return None  # Or handle the error differently

    def set_break_duration(self, break_type, duration):
        response = self.send_request(self.breaks_socket, "set_duration",
                                     {"break_type": break_type, "duration": duration})
        if response.get('status') == 'Duration Updated':
            messagebox.showinfo("Duration Updated", f"{break_type.capitalize()} break duration updated successfully!")
        else:
            messagebox.showerror("Update Error",
                                 f"Failed to update duration for {break_type}: {response.get('message', 'No details provided')}")


if __name__ == "__main__":
    app = PomodoroTimer()
    app.mainloop()
