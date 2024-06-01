import os, time, shutil, threading, re, pystray
from tkinter import Tk, Label, Entry, Button, StringVar, messagebox, filedialog
from PIL import Image, ImageDraw
from pystray import MenuItem as item

# Settings file
SETTINGS_FILE = "settings.txt"

# Default settings
downloads_folder = ""
interval = 0

# Function to handle the tray icon
def setup_tray_icon():
    icon = pystray.Icon("Junk Cleaner")
    icon.icon = create_image()
    icon.title = "Junk Cleaner"
    icon.menu = pystray.Menu(
        item('Settings', open_settings),
        item('Exit', exit_app)
    )
    icon.run()

# Function to exit the application
def exit_app(icon, item):
    icon.stop()

# Function to create an icon image
def create_image():
    width, height = 32, 32
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Define colors
    icon_color = (255, 255, 255, 255)  # White color for the icon

    # Draw computer screen
    screen_width, screen_height = 26, 20
    screen_x0, screen_y0 = (width - screen_width) // 2, (height - screen_height) // 2 - 2
    screen_x1, screen_y1 = screen_x0 + screen_width, screen_y0 + screen_height
    draw.rectangle([screen_x0, screen_y0, screen_x1, screen_y1], outline=icon_color, width=1)

    # Draw computer base
    base_width, base_height = 12, 2
    base_x0, base_y0 = (width - base_width) // 2, screen_y1
    base_x1, base_y1 = base_x0 + base_width, base_y0 + base_height
    draw.rectangle([base_x0, base_y0, base_x1, base_y1], outline=icon_color, width=1)

    # Draw computer stand
    stand_width, stand_height = 5, 3
    stand_x0, stand_y0 = (width - stand_width) // 2, base_y0 - stand_height
    stand_x1, stand_y1 = stand_x0 + stand_width, base_y0
    draw.rectangle([stand_x0, stand_y0, stand_x1, stand_y1], outline=icon_color, width=1)

    # Draw broom handle
    broom_x0, broom_y0 = screen_x0 + 4, screen_y0 + 4
    broom_x1, broom_y1 = broom_x0 + 8, broom_y0 + 16
    draw.line([broom_x0, broom_y0, broom_x1, broom_y1], fill=icon_color, width=1)

    # Draw broom head
    broom_head_width = 8
    broom_head_height = 4
    broom_head_x0 = broom_x1 - broom_head_width // 2
    broom_head_y0 = broom_y1
    broom_head_x1 = broom_head_x0 + broom_head_width
    broom_head_y1 = broom_head_y0 + broom_head_height
    draw.rectangle([broom_head_x0, broom_head_y0, broom_head_x1, broom_head_y1], outline=icon_color, width=1)

    # Draw broom bristles
    draw.line([broom_head_x0, broom_head_y1, broom_head_x0 - 2, broom_head_y1 + 2], fill=icon_color, width=1)
    draw.line([broom_head_x1, broom_head_y1, broom_head_x1 + 2, broom_head_y1 + 2], fill=icon_color, width=1)
    draw.line([(broom_head_x0 + broom_head_x1) // 2, broom_head_y1, (broom_head_x0 + broom_head_x1) // 2, broom_head_y1 + 4], fill=icon_color, width=1)

    return image

# Function to open the settings menu
def open_settings(icon=None, item=None):
    def browse_folder():
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            downloads_folder_var.set(folder_selected)

    def save_new_settings():
        global downloads_folder, interval
        downloads_folder = downloads_folder_var.get()
        interval_str = interval_var.get()
        interval = calculate_interval(interval_str)
        save_settings()
        settings_window.destroy()
        messagebox.showinfo("Settings", "Settings have been updated. They will be applied immediately and on next startup.")
        print(f"Settings updated: downloads_folder={downloads_folder}, interval={interval} seconds.")

    settings_window = Tk()
    settings_window.title("Settings")
    settings_window.geometry("300x200")

    downloads_folder_var = StringVar(value=downloads_folder)
    interval_var = StringVar(value=interval)

    Label(settings_window, text="Downloads Folder:").pack(pady=5)
    Entry(settings_window, textvariable=downloads_folder_var, width=40).pack(pady=5)
    Button(settings_window, text="Browse", command=browse_folder).pack(pady=5)

    Label(settings_window, text="Interval (e.g., 1h 2m 30s):").pack(pady=5)
    Entry(settings_window, textvariable=interval_var, width=40).pack(pady=5)

    Button(settings_window, text="Save", command=save_new_settings).pack(pady=20)

    settings_window.mainloop()

# Function to save settings to a file
def save_settings():
    with open(SETTINGS_FILE, 'w') as f:
        f.write(f"{downloads_folder}\n")
        f.write(f"{interval}\n")

# Function to load settings from a file
def load_settings():
    global downloads_folder, interval
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            downloads_folder = f.readline().strip()
            interval = int(f.readline().strip())

# Your main function that does some background work
def main_task():
    while True:
        clear_downloads_folder(downloads_folder)
        time.sleep(interval)

def clear_downloads_folder(downloads_folder):
    for filename in os.listdir(downloads_folder):
        file_path = os.path.join(downloads_folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

def calculate_interval(interval_str):
    time_units = {
        's': 1,
        'm': 60,
        'h': 3600,
        'd': 86400,
        'w': 604800
    }
    total_seconds = 0
    matches = re.findall(r'(\d+)([smhdw])', interval_str)
    for value, unit in matches:
        total_seconds += int(value) * time_units[unit]
    return total_seconds

def main():
    global downloads_folder, interval
    load_settings()

    if not downloads_folder or not interval:
        open_settings()

    # Run the main task in a separate thread
    task_thread = threading.Thread(target=main_task)
    task_thread.daemon = True
    task_thread.start()
    print(f"Started automatic deletion for {downloads_folder} every {interval} seconds.")

    # Set up the tray icon
    setup_tray_icon()

if __name__ == "__main__":
    main()