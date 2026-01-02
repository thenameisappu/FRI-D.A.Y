import cv2
import threading
import time
import os
import win32gui
import win32con


window_name = "Friday"
animation_running = True
current_text = ""
subtitle_end_time = 0 
image_size = (400, 400)

image_path = r"resources\images\friday_face\friday_face_image.jpg"
friday_images_paths = [rf"resources\images\friday_face\friday_{i}.png" for i in range(1, 5)]

face_img = cv2.imread(image_path)
friday_images = [cv2.imread(path) for path in friday_images_paths]

if face_img is None:
    raise Exception(f"Main face image not found at {image_path}")
if any(img is None for img in friday_images):
    missing_files = [friday_images_paths[i] for i, img in enumerate(friday_images) if img is None]
    raise Exception(f"Missing images: {', '.join(missing_files)}")

face_img = cv2.resize(face_img, image_size)
friday_images = [cv2.resize(img, image_size) for img in friday_images]


def wrap_text(text, font, max_width):
    lines = []
    words = text.split(' ')
    current_line = ""
    for word in words:
        test_line = current_line + ' ' + word if current_line else word
        test_size = cv2.getTextSize(test_line, font, 0.7, 2)[0]
        if test_size[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines


def add_subtitle(image, text):
    font = cv2.FONT_HERSHEY_SIMPLEX
    max_width = image.shape[1] - 40
    wrapped_text = wrap_text(text, font, max_width)
    y = image.shape[0] - 20 - (len(wrapped_text) * 30)
    img_copy = image.copy()
    
    overlay = img_copy.copy()
    for line in wrapped_text:
        text_size = cv2.getTextSize(line, font, 0.7, 2)[0]
        text_x = (image.shape[1] - text_size[0]) // 2
        cv2.rectangle(
            overlay,
            (text_x - 10, y - 20),
            (text_x + text_size[0] + 10, y + 10),
            (0, 0, 0),
            -1
        )
        y += 30
    
    cv2.addWeighted(overlay, 0.3, img_copy, 0.7, 0, img_copy)
    
    y = image.shape[0] - 20 - (len(wrapped_text) * 30)
    for line in wrapped_text:
        text_size = cv2.getTextSize(line, font, 0.7, 2)[0]
        text_x = (image.shape[1] - text_size[0]) // 2
        cv2.putText(img_copy, line, (text_x, y), font, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
        y += 30
    
    return img_copy


def animate_friday():
    global animation_running, current_text, subtitle_end_time

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    make_window_always_on_top(window_name)
    cv2.resizeWindow(window_name, 400, 400)
    cycle_sequence = list(range(4)) + list(range(2, 0, -1))

    while animation_running:
        for frame_idx in cycle_sequence:
            if not animation_running:
                break

            img = friday_images[frame_idx].copy()

            now = time.time()
            if current_text and (subtitle_end_time == 0 or now <= subtitle_end_time):
                img = add_subtitle(img, current_text)

            cv2.imshow(window_name, img)
            if cv2.waitKey(1) == 27:
                animation_running = False
                break

            time.sleep(0.5)


def start_animation():
    global animation_running
    animation_running = True
    animation_thread = threading.Thread(target=animate_friday, daemon=True)
    animation_thread.start()


def stop_animation():
    global animation_running
    animation_running = False
    cv2.destroyAllWindows()


def update_text(text):
    global current_text
    current_text = text

def make_window_always_on_top(window_name):
    time.sleep(0.2) 
    hwnd = win32gui.FindWindow(None, window_name)
    if hwnd:
        win32gui.SetWindowPos(
            hwnd,
            win32con.HWND_TOPMOST,
            0, 0, 0, 0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
        )



