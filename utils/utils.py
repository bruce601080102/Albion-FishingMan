import pygetwindow as gw
import cv2
import pyautogui
import numpy as np
import time
from PIL import Image, ImageTk
import warnings
warnings.filterwarnings("ignore")
pyautogui.FAILSAFE = False


def get_albion_windows():
    all_windows = gw.getAllWindows()
    x = 0
    y = 0
    width = 1040
    height = 807
    for win in all_windows:
        if "Albion" in win.title:
            # print(f"Title: {win.title}")
            # print(f"Location: {(win.left, win.top)}")
            # print(f"Size: {(win.width, win.height)}")
            # print("-" * 40)
            x = win.left
            y = win.top
            width = win.width
            height = win.height
            return x, y, width, height


def photoimage_to_pil_image(photoimage):
    return ImageTk.getimage(photoimage)


def pil_image_to_nparray(pil_image):
    return np.array(pil_image)


def photoimage_to_nparray(photoimage):
    pil_image = photoimage_to_pil_image(photoimage)
    return pil_image_to_nparray(pil_image)


class FishAction:
    def __init__(self):
        self.pyautogui = pyautogui
        # self.target_image, self.h, self.w = self.read_image('./images/label1.png')
        self.target_image, self.h, self.w = self.read_image('./images/label2.png')
        
    def read_image(self, template_image_path):
        target_image = cv2.imread(template_image_path, cv2.IMREAD_COLOR)
        h, w = target_image.shape[:2]
        return target_image, h, w
        
    def casting_rod_action(self, x_position, y_position, sec=0.5):
        pyautogui.mouseUp(x_position, y_position, button='left')
        pyautogui.mouseDown(x_position, y_position, button='left')
        time.sleep(sec)
        pyautogui.mouseUp(x_position, y_position, button='left')

    def start_casting_rod(self, direction):
        x, y, width, height = get_albion_windows()
        
        x_position = (x + width) // 2
        y_position = (y + height) // 2 - 20
        pool_direction = direction
        click_sec = 0.5
        if pool_direction == "left":
            x_position = x_position - 200
            self.casting_rod_action(x_position, y_position, click_sec)

        elif pool_direction == "right":
            x_position = x_position + 200
            self.casting_rod_action(x_position, y_position, click_sec)

        elif pool_direction == "top":
            y_position = y_position - 200
            self.casting_rod_action(x_position, y_position, click_sec)
        return x_position, y_position, pool_direction

    def start_finshing(self, type_image, cv_threshold):
        frame = photoimage_to_nparray(type_image)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        res = cv2.matchTemplate(frame, self.target_image, cv2.TM_CCOEFF_NORMED)

        # Set a threshold value for the match
        threshold = cv_threshold
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        
        top_left = max_loc
        bottom_right = (top_left[0] + self.w, top_left[1] + self.h)
        object_position = None

        cv2.rectangle(frame, (420, 390), (600, 460), (0, 255, 0), 2)  # 釣魚alert的視窗位置
        if max_val > threshold:
            if bottom_right[0] >= 420 and bottom_right[0] <= 600 and bottom_right[1] >= 390 and bottom_right[1] <= 460:
                object_position = bottom_right
                cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_frame)
        photo_image = ImageTk.PhotoImage(pil_image)
        
        return photo_image, object_position

    def _click_finshing(self, lake_position_x, lake_position_y):
        def hold_right_click_for_1_second():
            time.sleep(0.15)  
            pyautogui.mouseDown(lake_position_x, lake_position_y, button='left')
            time.sleep(1.25)
            pyautogui.mouseUp(lake_position_x, lake_position_y, button='left')
            # 0.9,3 放開按住的比例 釣垃圾
            
        hold_right_click_for_1_second()


if __name__ == "__main__":
    fa = FishAction()
    fa.start_casting_rod()
