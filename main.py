import tkinter as tk
from PIL import Image, ImageTk
import subprocess
import os
import signal
import sys
import platform


def display_image_with_text(image_path, jar_path, text_to_insert):
    # Run the Java process at the start
    java_process = subprocess.Popen(["java", "-jar", jar_path],
                                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0)

    # Function to safely terminate the Java process on close
    def on_close():
        if java_process.poll() is None:  # Check if the process is still running
            if platform.system() == "Windows":
                os.kill(java_process.pid, signal.CTRL_BREAK_EVENT)  # Graceful termination for Windows
            elif platform.system() in ["Linux", "Darwin"]:  # Darwin is macOS
                os.kill(java_process.pid, signal.SIGTERM)  # Terminate process on Linux/MacOS
        window.destroy()

    # Create a tkinter window
    window = tk.Tk()
    window.title("Image with Text")
    window.configure(bg="black")

    # Load the image using PIL
    image = Image.open(image_path)
    img_width, img_height = image.size

    # Convert the image to a Tkinter-compatible PhotoImage
    tk_image = ImageTk.PhotoImage(image)

    # Set the window size based on the image dimensions
    window.geometry(f"{img_width}x{img_height}")

    # Create a canvas to display the image
    canvas = tk.Canvas(window, width=img_width, height=img_height, highlightthickness=0, bg="black")
    canvas.pack()

    # Display the image on the canvas
    canvas.create_image(0, 0, anchor=tk.NW, image=tk_image)

    # Add the overlay text
    canvas.create_text(img_width // 2, img_height // 2, text=text_to_insert, fill="white",
                       font=("Helvetica", 24, "bold"))

    # Bind the close event to terminate the Java process
    window.protocol("WM_DELETE_WINDOW", on_close)

    # Run the tkinter main loop
    window.mainloop()


# Main entry point of the script
if __name__ == "__main__":
    # Get the parameters from the command line
    image_path = "background.webp"
    jar_path = "fat.jar"
    text_to_insert = "sys.argv[3]"

    # Run the program
    display_image_with_text(image_path, jar_path, text_to_insert)
