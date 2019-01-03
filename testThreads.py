import time
import tkinter as tk
import tkinter.ttk as ttk
import queue
import threading

class GUI:
    def __init__(self, master):
        self.master = master
        self.test_button = tk.Button(self.master, command=self.tb_click)
        self.test_button.configure(
            text="Start", background="Grey",
            padx=50
            )
        self.test_button.pack(side=tk.TOP)

    def progress(self):
        self.prog_bar = ttk.Progressbar(
            self.master, orient="horizontal",
            length=200, mode="indeterminate"
            )
        self.prog_bar.pack(side=tk.TOP)

    def tb_click(self):
        self.progress()
        self.prog_bar.start()
        self.queue = queue.Queue()
        ThreadedTask(self.queue).start()
        self.master.after(100, self.process_queue)

    def process_queue(self):
        try:
            msg = self.queue.get(0)
            # Show result of the task if needed
            self.prog_bar.stop()
        except queue.Empty:
            self.master.after(100, self.process_queue)
            
class ThreadedTask(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
    def run(self):
        time.sleep(5)  # Simulate long running process
        self.queue.put("Task finished")

root = tk.Tk()
root.title("Test Button")
main_ui = GUI(root)
root.mainloop()
