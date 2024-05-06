import tkinter as tk
from tkinter import ttk, simpledialog, PhotoImage, messagebox
import time
import zmq

class PomodoroTimer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pomodoro App")
        self.geometry("300x500")
        self.configure(bg='#BACD92')

        # Setup ZeroMQ for communication
        self.context = zmq.Context()
        self.task_socket = self.context.socket(zmq.REQ)
        self.task_socket.connect("tcp://localhost:5558")

        self.durations = {'pomodoro': 1500, 'short_break': 300, 'long_break': 900}
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
            ttk.Button(mode_frame, text=mode.capitalize(), command=lambda m=mode: self.switch_mode(m)).pack(side=tk.LEFT)

        # -----------------------------------------------------------
        # TASK MANAGEMENT
        # -----------------------------------------------------------
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

    def refresh_tasks(self):
        for widget in self.task_frame.winfo_children():
            widget.destroy()

        for i, task in enumerate(self.tasks):
            self.create_task_widget(i, task)


    def add_task(self):
        task_description = self.task_entry.get()
        if task_description:
            self.tasks.append({"description": task_description, "completed": False})
            self.task_entry.delete(0, tk.END)
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
        new_description = simpledialog.askstring("Edit Task", "Edit the task description:", initialvalue=self.tasks[index]['description'])
        if new_description:
            self.tasks[index]['description'] = new_description
            self.refresh_tasks()

    def delete_task(self, index):
        del self.tasks[index]
        self.refresh_tasks()
    def toggle_task(self, index, var):
        self.tasks[index]['completed'] = var.get()
        self.refresh_tasks()

    def confirm_delete_task(self, index):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this task?"):
            self.delete_task(index)

    # Send a request to the server via ZeroMQ
    def send_request(self, socket, action, data):
        socket.send_json({'action': action, **data})
        return socket.recv_json()

    # -----------------------------------------------------------
    # SETTINGS SERVICE
    # -----------------------------------------------------------
    def open_settings(self):
        settings_window = tk.Toplevel(self)
        settings_window.title("Timer Settings")
        settings_window.geometry("250x150")
        settings_window.configure(background='#F5DAD2')

        row = 0
        entries = {}
        for mode, seconds in self.durations.items():
            label = ttk.Label(settings_window, text=f"{mode.capitalize()} duration (minutes):")
            label.grid(row=row, column=0, padx=10, pady=5)
            entry = ttk.Entry(settings_window, width=5)
            entry.insert(0, seconds // 60)
            entry.grid(row=row, column=1, padx=5)
            entries[mode] = entry
            row += 1

        def save_settings():
            for mode, entry in entries.items():
                self.durations[mode] = int(entry.get()) * 60
                if self.current_timer == mode:  # Update current timer if its duration was changed
                    self.switch_mode(mode)
            settings_window.destroy()

        save_button = ttk.Button(settings_window, text="Save", command=save_settings)
        save_button.grid(row=row, column=0, columnspan=2, pady=10)

    # -----------------------------------------------------------
    # TIMER AND BREAKS SERVICES
    # -----------------------------------------------------------
    def start_or_pause_timer(self):
        if not self.running:
            self.start_timer()
        elif self.paused:
            self.resume_timer()
        else:
            self.pause_timer()

    def start_timer(self):
        self.running = True
        self.paused = False
        self.start_time = time.time()
        self.update_timer()
        self.control_button.config(text="Pause")

    def pause_timer(self):
        self.paused = True
        self.control_button.config(text="Resume")

    def resume_timer(self):
        if not self.running:
            return
        self.paused = False
        self.start_time = time.time() - (self.durations[self.current_timer] - self.remaining_time)
        self.update_timer()
        self.control_button.config(text="Pause")

    def update_timer(self):
        if self.running and not self.paused:
            elapsed = time.time() - self.start_time
            self.remaining_time = max(0, self.durations[self.current_timer] - int(elapsed))
            self.timer_display.config(text=self.format_time(self.remaining_time))
            if self.remaining_time > 0:
                self.after(1000, self.update_timer)
            else:
                self.reset_timer()

    def reset_timer(self):
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




if __name__ == "__main__":
    app = PomodoroTimer()
    app.mainloop()
