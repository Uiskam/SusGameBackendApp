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
                print(f"Port {port} is in use. Trying next port...")
                port += 1
        except Exception as e:
            print(f"An error occurred: {e}")
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
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
    )

    def on_close():
        if java_process.poll() is None:  # Check if the process is still running
            pass
            # java_process.terminate()
        root.destroy()

    def toggle_logs():
        if log_frame.winfo_ismapped():
            log_frame.pack_forget()
            log_button.config(text="Display Logs")
        else:
            log_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
            log_button.config(text="Hide Logs")

    # Create a tkinter root
    root = tk.Tk()
    root.title("SusGame Server")
    root.configure(bg="black")
    max_width, max_height = root.maxsize()

    image = Image.open(image_path)
    img_width, img_height = image.size
    offset = 100
    final_width, final_height = (min(img_width, max_width) - offset, min(img_height, max_height) - offset)

    image = image.resize((final_width, final_height - 100))

    tk_image = ImageTk.PhotoImage(image)
    root.geometry(f"{final_width}x{final_height}")

    canvas = tk.Canvas(root, width=final_width, height=final_height, highlightthickness=0, bg="black")
    canvas.pack()
    canvas.create_image(0, 0, anchor=tk.NW, image=tk_image)
    canvas.create_text(final_width // 2, final_height // 2, text=text_to_insert, fill="white",
                       font=("Helvetica", 24, "bold"))

    # Scrollable text widget for logs
    log_frame = tk.Frame(root, bg="black")
    log_text_widget = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=100, bg="black", fg="white",
                                                font=("Courier", 10))
    log_text_widget.pack(fill=tk.BOTH, expand=True)

    # Start a thread to read stderr
    stderr_thread = threading.Thread(target=read_stderr, args=(java_process.stderr, log_text_widget))
    stderr_thread.daemon = True
    stderr_thread.start()

    # Add button to toggle logs
    log_button = tk.Button(root, text="Display Logs", command=toggle_logs, bg="white", fg="black",
                           font=("Helvetica", 12, "bold"))
    log_button.place(x=0, y=final_height - 50, anchor=tk.SW)

    # Bind the close event to terminate the Java process
    root.protocol("WM_DELETE_WINDOW", on_close)

    root.mainloop()


# Main entry point of the script
if __name__ == "__main__":
    image_path = "background.png"
    jar_path = "CyberSurfers.jar"
    unused_port = find_unused_port()
    text_to_insert = get_ip() + f":{unused_port}"
    os.environ["PORT"] = str(unused_port)

    # Run the program
    display_image_with_text(image_path, jar_path, text_to_insert)
