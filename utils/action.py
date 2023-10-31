import tkinter as tk
import numpy as np
import time
import threading
from PIL import ImageGrab, ImageTk
from utils.utils import FishAction
import configparser


class DraggableBox(tk.Toplevel):
    def __init__(self, parent, init_logger, box_width=100, box_height=100, direction="top", config_path=None):
        super().__init__(parent)
        self.config_path = config_path
        self.config = configparser.ConfigParser()
        self.config.read(self.config_path)

        self.init_logger = init_logger
        self.direction = direction
        self.fa = FishAction()
        self.bound_box_xy = None
        self.is_fishing = False
        window_width = 1024
        window_height = 500
        self.geometry(f'{window_width}x{window_height}')
        self.resizable(False, False)
        self.title("FishingMan Window")
        
        self.box_width = box_width
        self.box_height = box_height
        self.start_action = 0
        self.lock_bool = False
        self.is_fishing_finally = False
        
        self.record_times_ratio_list = []
        self.record_times = 0
        self.record_value = 1
        self.record_value_ratio = 1
        self.record_fishing_times = 0
        self.record_all_fishing_times = 0
        self.record_result = {"success": 0, "trash": 0, "fail": 0}
        
        self.threshold = 1
        self.record_fail_times = 0
        self.diff_ratio_threshold = 1.02
        self.list_train_data_ratio = []

        self.attributes('-transparentcolor', 'white')

        self.canvas = tk.Canvas(self, cursor="hand2", bg='white', bd=0, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.box_x = window_width - box_width
        self.box_y = window_height - box_height
        self.config.set('conf', 'box_x', f"{self.box_x}")
        self.config.set('conf', 'box_y', f"{self.box_y}")
        # print(self.box_x, self.box_y)
        with open(self.config_path, 'w') as configfile:
            self.config.write(configfile)
        self.top_x = self.config.getfloat('fishing_direction', 'top_x')
        self.top_y = self.config.getfloat('fishing_direction', 'top_y')
        self.left_x = self.config.getfloat('fishing_direction', 'left_x')
        self.left_y = self.config.getfloat('fishing_direction', 'left_y')
        self.right_x = self.config.getfloat('fishing_direction', 'right_x')
        self.right_y = self.config.getfloat('fishing_direction', 'right_y')
        self.cv_threshold = self.config.getfloat('conf', 'cv_threshold')

        self.rect = self.canvas.create_rectangle(self.box_x, self.box_y, self.box_x + box_width, self.box_y + box_height, outline='red', width=2)

        self.current_box_x = self.box_x
        self.current_box_y = self.box_y
        self.detect_times_fishing_complete = 0

        self.canvas.tag_bind(self.rect, "<Button-1>", self.on_box_click)
        self.canvas.tag_bind(self.rect, "<B1-Motion>", self.on_box_drag)
        self.canvas.tag_bind(self.rect, "<ButtonRelease-1>", self.move_init_record_value)
        self.bind('<Return>', self.formal_start_fishing)

        self.bind('<Escape>', self.exit_program)
        self.bind('<F5>', self.start_casting_rod)
        self.bind('<F6>', self.detecting_hooking_characteristics)
        self.update_background()

    def start_casting_rod(self, event):
        def muti_func(event):
            self.pyautogui = self.fa.pyautogui
            self.x_position, self.y_position, pool_direction = self.fa.start_casting_rod(self.direction)
            if pool_direction == "top":
                self.auto_move_box(event, round(self.box_x * self.top_x), round(self.box_y * self.top_y))
            elif pool_direction == "left":
                self.auto_move_box(event, round(self.box_x * self.left_x), round(self.box_y * self.left_y))
            elif pool_direction == "right":
                self.auto_move_box(event, round(self.box_x * self.right_x), round(self.box_y * self.right_y))
        thread = threading.Thread(target=muti_func, args=(event,))
        thread.start()
        
    def update_background(self):
        x, y, w, h = self.canvas.bbox("all")
        im = ImageGrab.grab(bbox=(x, y, w, h))
        self.bg_img = ImageTk.PhotoImage(im)
        self.lock_bool = False
        # if self.is_fishing:
        self.bg_img, self.bound_box_xy = self.fa.start_finshing(self.bg_img, self.cv_threshold)
        if self.is_fishing and self.bound_box_xy is not None:
            thread = threading.Thread(target=self.fa._click_finshing, args=(self.x_position, self.y_position,))
            thread.start()
            thread.join()
            self.detect_times_fishing_complete += 1
        elif self.is_fishing and self.bound_box_xy is None:
            if self.detect_times_fishing_complete in [1, 2, 3]:
                self.init_logger.info("掉垃圾")
                self.record_result["trash"] += 1
                time.sleep(3)
                self.formal_start_fishing()
                self.detect_times_fishing_complete = 0
                self.record_fishing_times = 0
            elif self.detect_times_fishing_complete == 0:
                self.init_logger.info("判斷錯誤")
                self.record_result["fail"] += 1
                time.sleep(5)
                self.formal_start_fishing()
                self.detect_times_fishing_complete = 0
                self.record_fishing_times = 0
            elif self.detect_times_fishing_complete >= 4:
                self.init_logger.info("釣魚完成")
                self.record_result["success"] += 1
                time.sleep(3)
                self.formal_start_fishing()
                self.detect_times_fishing_complete = 0
                self.record_fishing_times = 0

        self.canvas.create_image(0, 0, image=self.bg_img, anchor=tk.NW)
        self.canvas.tag_raise(self.rect)
        self.after(200, self.update_background)

    def on_box_click(self, event):
        self.click_x = event.x
        self.click_y = event.y

    def on_box_drag(self, event):
        dx = event.x - self.click_x
        dy = event.y - self.click_y

        self.canvas.move(self.rect, dx, dy)
        self.current_box_x += dx
        self.current_box_y += dy
        print("紅框位置: ", self.current_box_x, self.current_box_y)
        self.click_x = event.x
        self.click_y = event.y
        
    def auto_move_box(self, event, target_x, target_y):
        dx = target_x - self.current_box_x
        dy = target_y - self.current_box_y

        self.canvas.move(self.rect, dx, dy)
        self.current_box_x = target_x
        self.current_box_y = target_y

    def detecting_hooking_characteristics(self, event=None):
        self.record_fishing_times += 1
        x1, y1, x2, y2 = self.canvas.coords(self.rect)
        im = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        current_img = np.sum(im, dtype=np.int64)

        if abs(current_img) > abs(self.record_value):
            diff = abs(current_img) / abs(self.record_value)
        else:
            diff = abs(self.record_value) / abs(current_img)
        if self.record_times > 3:
            if abs(self.record_value_ratio) > abs(diff):
                diff_ratio = abs(self.record_value_ratio) / abs(diff)
            else:
                diff_ratio = abs(diff) / abs(self.record_value_ratio)
            # print("diff_ratio: ", diff_ratio)
            if diff_ratio >= self.diff_ratio_threshold:
                self.init_logger.info("Fishing is active")
                self.start_action += 1
            else:
                self.record_times_ratio_list.append(diff_ratio)
                self.start_action = 0
                # print("還不能釣魚")
            # self.list_train_data_ratio.append(diff_ratio)
        self.record_value = current_img
        self.record_value_ratio = diff
        self.record_times += 1

        if self.start_action < self.threshold:
            if self.record_fail_times % 100 == 1 and self.record_fail_times != 1:
                self.diff_ratio_threshold = max(self.record_times_ratio_list)
                self.record_times_ratio_list.clear()
                self.init_logger.info(f"change ratio: {self.diff_ratio_threshold}")
            self.record_fail_times += 1
            self.is_fishing = False
            self.after(500, self.detecting_hooking_characteristics)
        elif self.record_fishing_times > 5 and self.start_action >= self.threshold:
            self.init_logger.info("The act of hooking the fish")
            self.start_action = 0
            self.init_record_value(event)
            self.pyautogui.click(self.x_position, self.y_position)
            self.is_fishing = True
            time.sleep(0.1)  # 必要,需要給程式判斷物體
        else:
            self.after(500, self.detecting_hooking_characteristics)

    def exit_program(self, event=None):
        self.destroy()

    def formal_start_fishing(self, event=None):
        self.record_all_fishing_times += 1
        self.init_logger.info(f"Fishing for the {self.record_all_fishing_times}th time")
        self.init_logger.info(f"Show current fishing status: {self.record_result}")
        self.start_casting_rod(event)
        self.detecting_hooking_characteristics(event)

    def init_record_value(self, event=None):
        self.record_times = 0
        self.record_value = 1
        self.record_value_ratio = 1
        self.start_action = 0
        self.record_fail_times = 0

    def move_init_record_value(self, event=None):
        self.record_result = {"success": 0, "trash": 0, "fail": 0}
        self.config.set('fishing_direction', f'{self.direction}_x', f"{self.current_box_x/self.box_x}")
        self.config.set('fishing_direction', f'{self.direction}_y', f"{self.current_box_y/self.box_y}")
        with open(self.config_path, 'w') as configfile:
            self.config.write(configfile)

        self.record_times_ratio_list = []
        self.diff_ratio_threshold = 1.02
        self.record_times = 0
        self.record_value = 1
        self.record_value_ratio = 1
        self.start_action = 0
        self.threshold = 1
        self.record_fail_times = 0
