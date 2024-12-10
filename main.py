import tkinter as tk
from tkinter import scrolledtext
from PIL import Image, ImageTk
import subprocess
import os
import socket
import threading
import platform


def find_unused_port(start_port=8080) -> int:
    """
    Finds an unused port starting from the given port.

    :param start_port: The initial port to check.
    :return: An unused port number.
    """
    port = start_port
    is_windows = platform.system().lower() == "windows"

    while True:
        try:
            # Choose the appropriate command for Windows or Linux
            if is_windows:
                command = f'netstat -ano | findstr :{port}'
            else:
                command = f'netstat -tuln | grep :{port}'
            # Run the command
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                shell=True
            )

            # If the command output is empty, the port is not in use
            if not result.stdout:
                return port
            else:
                # If output is not empty, increment the port number
                port += 1
        except Exception as _:
            return 8080


def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        return f"Error: {e}"


def read_stderr(pipe, log_widget):
    with pipe:
        for line in iter(pipe.readline, b''):
            log_text = line.decode().strip()
            log_widget.insert(tk.END, log_text + "\n")
            log_widget.see(tk.END)


def display_image_with_text(image_path, jar_path, text_to_insert):
    # Run the Java process at the start
    java_process = subprocess.Popen(
        ["java", "-jar", jar_path],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
    )

    def on_close():
        if java_process.poll() is None:
            java_process.terminate()
            java_process.kill()
        window.destroy()

    def toggle_logs():
        if log_frame.winfo_ismapped():
            canvas.config(height=max_height)
            log_frame.pack_forget()
            log_button.config(text="Display Logs")
            log_button.place(x=0, y=max_height - 20, anchor=tk.SW)
        else:
            canvas.config(height=image_frame_height)
            log_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
            log_button.config(text="Hide Logs")
            log_button.place(x=0,y=image_frame_height-20, anchor=tk.SW)

    # Create a tkinter window
    window = tk.Tk()
    window.title("CyberSurfers Server")
    window.configure(bg="black")
    window_padding = 30
    image = Image.open(image_path)
    img_width, img_height = image.size
    max_width, max_height = window.maxsize()
    max_width, max_height = min(max_width, img_width) - window_padding, min(max_height, img_height) - window_padding
    image_frame_height = int(max_height * (2/3))
    image_frame_width = max_width
    log_frame_height = max_height - image_frame_height
    window.geometry(f"{max_width}x{max_height}")


    image_frame = tk.Frame(window, bg="black")
    # image = image.resize((max_width, int((img_height/img_width) * max_width)))
    image = image.resize((max_width, max_height))
    tk_image = ImageTk.PhotoImage(image)
    canvas = tk.Canvas(image_frame, width=image_frame_width, height=max_height, highlightthickness=0, bg="black")
    ip_font_size = image_frame_height // 10
    title_font_size = ip_font_size * 2
    canvas.create_image(0, 0, anchor=tk.NW, image=tk_image)
    canvas.create_text(image_frame_width // 2, max_height // 2, text=text_to_insert, fill="white",
                       font=("VT323", ip_font_size))
    canvas.create_text(image_frame_width // 2, title_font_size, text="CyberSurfers", fill="white",
                       font=("VT323", title_font_size))
    # Add button to toggle logs
    log_button = tk.Button(image_frame, text="Display Logs", command=toggle_logs, bg="white", fg="black",
                           font=("Helvetica", 12, "bold"))
    log_button.place(x=0,y=max_height-24,anchor=tk.SW)
    canvas.pack()
    image_frame.pack(fill=tk.BOTH)

    # Scrollable text widget for logs
    log_frame = tk.Frame(window, bg="black", height=log_frame_height)
    log_text_widget = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=100, bg="black", fg="white",
                                                font=("Courier", 10))
    log_text_widget.pack(fill=tk.BOTH, expand=True)

    # Start a thread to read stderr
    stderr_thread = threading.Thread(target=read_stderr, args=(java_process.stderr, log_text_widget))
    stderr_thread.daemon = True
    stderr_thread.start()

    stdout_thread = threading.Thread(target=read_stderr, args=(java_process.stdout, log_text_widget))
    stdout_thread.daemon = True
    stdout_thread.start()

    # Bind the close event to terminate the Java process
    window.protocol("WM_DELETE_WINDOW", on_close)
    window.mainloop()


# Main entry point of the script
if __name__ == "__main__":
    image_path = "background.png"
    jar_path = "CyberSurfers.jar"
    unused_port = find_unused_port()
    text_to_insert = get_ip() + f":{unused_port}"
    os.environ["PORT"] = str(unused_port)

    # Run the program
    display_image_with_text(image_path, jar_path, text_to_insert)
