import tkinter as tk
from tkinter import ttk
from utils.action import DraggableBox
from utils.log import LogHandler
from PIL import Image, ImageTk


log_handler = LogHandler(service='Fishingman')
init_logger = log_handler.getlogger('INIT')
init_logger.info("success log")


class MainGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("FishingMan")
        self.root.geometry('300x100')
        self.root.resizable(False, False)
        icon_image = Image.open("./images/icon.png")
        icon_photo = ImageTk.PhotoImage(icon_image)
        self.root.tk.call('wm', 'iconphoto', self.root._w, icon_photo)

    def gui_struct(self):
        label2_casting_direction = ttk.LabelFrame(self.root, text='select toss direction')
        self.direct_bobox = ttk.Combobox(label2_casting_direction, state='readonly', width=25)

        directList = ["top", "right", "left"]
        self.direct_bobox['values'] = directList

        label2_casting_direction.pack(side=tk.TOP, expand=tk.YES)
        self.direct_bobox.pack(side=tk.TOP, expand=tk.YES, pady=10)

        start_button = tk.Button(self.root, text="Start", command=self.start_app)
        start_button.pack(side=tk.TOP)

    def start_app(self):
        selected_direction = self.direct_bobox.get()
        DraggableBox(self.root, init_logger=init_logger, direction=selected_direction, config_path='./conf/conf.txt')

    @property
    def run(self):
        self.gui_struct()
        self.root.mainloop()


if __name__ == "__main__":
    main_gui = MainGUI()
    main_gui.run()
