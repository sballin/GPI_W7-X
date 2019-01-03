'''
Stripped down example version of the gui program updating a plot in an arbitrary grid cell in python3 tkinter.

Original source: https://matplotlib.org/gallery/user_interfaces/embedding_in_tk_sgskip.html
'''
import tkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import time
import threading
import random

class FakeRedPitaya(object):
    def __getattr__(self, name):
        '''
        Returns 0 for all Red Pitaya functions instead of raising errors.
        '''
        def method(*args):
            return random.random()
        return method

class GUI:
    def __init__(self, root):
        self.root = root
        self.points = 10
        self.GPI = FakeRedPitaya()
        self.data1 = [self.GPI.get_asdf() for i in range(self.points)]
        self.data2 = [self.GPI.get_asdf() for i in range(self.points)]

        # Example elements to show that the grid is working
        elem1 = tkinter.Label(bg='green')
        elem1.grid(row=1, column=1)
        elem2 = tkinter.Label(bg='red')
        elem2.grid(row=2, column=3)

        # Plot matplotlib setup
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax1 = self.fig.add_subplot(211)
        self.line1, = self.ax1.plot(self.data1)
        self.ax2 = self.fig.add_subplot(212)
        self.line2, = self.ax2.plot(self.data2)

        # Plot tkinter setup
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)  # A tk.DrawingArea.
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=3,column=2)

        t = threading.Thread(target=self.generate_data, daemon=True)
        t.start()
        self.update_plot()
    
    def generate_data(self):
        while True:
            self.data1.append(self.GPI.get_asdf())
            self.data2.append(self.GPI.get_asdf())
            time.sleep(0.4)
        
    def update_plot(self):
        print(self.line1.get_data())
        # self.line1.set_data(range(len(self.data1)), self.data1)
        # self.line2.set_data(range(len(self.data1)), self.data2)
        self.ax1.cla()
        self.ax1.plot(self.data1)
        self.ax2.cla()
        self.ax2.plot(self.data2)
        self.fig.canvas.draw_idle()
        self.root.after(500, self.update_plot)


root = tkinter.Tk()
main_ui = GUI(root)
root.mainloop()
