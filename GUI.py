import tkinter as tk
from tkinter import filedialog
import cv2
from PIL import Image, ImageTk
import numpy as np
import threading
import time

# Initialize Tkinter window
window = tk.Tk()
window.title("Video Synchronization Tool")
window.geometry("900x700")

# Global variables to hold video paths and frame counters
left_video_path = ""
right_video_path = ""
current_frame_left = 0
current_frame_right = 0
left_cap = None
right_cap = None
left_playing = False
right_playing = False

# Function to load left video
def load_left_video():
    global left_video_path, left_cap, current_frame_left
    left_video_path = filedialog.askopenfilename(title="Select Left Video", filetypes=[("MP4 Files", "*.mp4")])
    if left_video_path:
        left_video_label.config(text="Left Video Loaded: " + left_video_path.split("/")[-1])
        left_cap = cv2.VideoCapture(left_video_path)
        display_video_frame(left_video_path, left_frame_label)
        current_frame_left = 0  # Reset frame counter when new video is loaded

# Function to load right video
def load_right_video():
    global right_video_path, right_cap, current_frame_right
    right_video_path = filedialog.askopenfilename(title="Select Right Video", filetypes=[("MP4 Files", "*.mp4")])
    if right_video_path:
        right_video_label.config(text="Right Video Loaded: " + right_video_path.split("/")[-1])
        right_cap = cv2.VideoCapture(right_video_path)
        display_video_frame(right_video_path, right_frame_label)
        current_frame_right = 0  # Reset frame counter when new video is loaded

# Function to display a frame from each video
def display_video_frame(video_path, label):
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Set to the start
    ret, frame = cap.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        img = img.resize((300, 200))  # Resize for display
        img_tk = ImageTk.PhotoImage(img)
        label.config(image=img_tk)
        label.image = img_tk  # Keep a reference to avoid garbage collection
    cap.release()

# Function to continuously play the left video forward
def advance_left():
    global current_frame_left, left_cap, left_playing
    if left_cap and not left_playing:
        left_playing = True
        new_window = tk.Toplevel(window)
        new_window.title("Advancing Left Video")
        
        new_frame_label = tk.Label(new_window)
        new_frame_label.pack()

        threading.Thread(target=move_left_in_window, args=(new_window, new_frame_label, False)).start()

# Function to continuously reverse the left video
def reverse_left():
    global current_frame_left, left_cap, left_playing
    if left_cap and current_frame_left > 0 and not left_playing:
        left_playing = True
        new_window = tk.Toplevel(window)
        new_window.title("Reversing Left Video")
        
        new_frame_label = tk.Label(new_window)
        new_frame_label.pack()

        threading.Thread(target=move_left_in_window, args=(new_window, new_frame_label, True)).start()

# Function to continuously play the right video forward
def advance_right():
    global current_frame_right, right_cap, right_playing
    if right_cap and not right_playing:
        right_playing = True
        new_window = tk.Toplevel(window)
        new_window.title("Advancing Right Video")
        
        new_frame_label = tk.Label(new_window)
        new_frame_label.pack()

        threading.Thread(target=move_right_in_window, args=(new_window, new_frame_label, False)).start()

# Function to continuously reverse the right video
def reverse_right():
    global current_frame_right, right_cap, right_playing
    if right_cap and current_frame_right > 0 and not right_playing:
        right_playing = True
        new_window = tk.Toplevel(window)
        new_window.title("Reversing Right Video")
        
        new_frame_label = tk.Label(new_window)
        new_frame_label.pack()

        threading.Thread(target=move_right_in_window, args=(new_window, new_frame_label, True)).start()

# Function to move the left video forward or backward in the new window
def move_left_in_window(new_window, new_frame_label, reverse=False):
    global current_frame_left, left_cap
    while left_playing:
        if new_window.winfo_exists():  # Check if the window is still open
            if reverse:
                if current_frame_left > 0:
                    current_frame_left -= 1
                    left_cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame_left)
                    ret, frame = left_cap.read()
                    if ret:
                        display_video_frame_in_window(new_frame_label, frame)
            else:
                current_frame_left += 1
                left_cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame_left)
                ret, frame = left_cap.read()
                if ret:
                    display_video_frame_in_window(new_frame_label, frame)
            time.sleep(0.05)  # Faster frame update speed
        else:
            break  # Stop the loop if the window is closed

# Function to move the right video forward or backward in the new window
def move_right_in_window(new_window, new_frame_label, reverse=False):
    global current_frame_right, right_cap
    while right_playing:
        if new_window.winfo_exists():  # Check if the window is still open
            if reverse:
                if current_frame_right > 0:
                    current_frame_right -= 1
                    right_cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame_right)
                    ret, frame = right_cap.read()
                    if ret:
                        display_video_frame_in_window(new_frame_label, frame)
            else:
                current_frame_right += 1
                right_cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame_right)
                ret, frame = right_cap.read()
                if ret:
                    display_video_frame_in_window(new_frame_label, frame)
            time.sleep(0.05)  # Faster frame update speed
        else:
            break  # Stop the loop if the window is closed

# Function to display video frames in a new window
def display_video_frame_in_window(new_frame_label, frame):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame)
    img = img.resize((300, 200))  # Resize for display
    img_tk = ImageTk.PhotoImage(img)
    new_frame_label.config(image=img_tk)
    new_frame_label.image = img_tk  # Keep a reference to avoid garbage collection

# Function to process and combine the videos
def process_and_combine():
    if not left_video_path or not right_video_path:
        print("Both videos need to be loaded.")
        return

    # Open the left and right video files
    global left_cap, right_cap
    left_cap = cv2.VideoCapture(left_video_path)
    right_cap = cv2.VideoCapture(right_video_path)

    # Get frame rate and frame dimensions
    fps_left = left_cap.get(cv2.CAP_PROP_FPS)
    fps_right = right_cap.get(cv2.CAP_PROP_FPS)
    frame_width_left = int(left_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height_left = int(left_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    frame_width_right = int(right_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height_right = int(right_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Output video setup
    target_width = 900
    target_height = 640
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    output_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 Files", "*.mp4")])
    out = cv2.VideoWriter(output_path, fourcc, fps_left, (target_width, target_height))

    # Offset adjustment
    offset = 10  # Adjust this to sync the videos
    shift_amount = 20  # Horizontal shift for right video
    overlap_width = 475  # Overlap width for blending
    bottom_shift = 10  # Shift for bottom alignment

    # Process video frames
    while True:
        ret_left, frame_left = left_cap.read()
        ret_right, frame_right = right_cap.read()

        if not ret_left or not ret_right:
            break

        # Resize and process frames
        frame_left = cv2.resize(frame_left, (frame_width_left, frame_height_left))
        frame_right = cv2.resize(frame_right, (frame_width_right, frame_height_right))

        # Apply offset by skipping frames from left video
        if offset > 0:
            for _ in range(offset):
                ret_left, frame_left = left_cap.read()  # Skip frames from left video
            offset = 0  # Reset offset after skipping

        # Shift right video horizontally
        frame_right_shifted = np.zeros_like(frame_right)
        frame_right_shifted[:, shift_amount:] = frame_right[:, :-shift_amount]

        # Shift the right video down for alignment
        if bottom_shift != 0:
            shifted_frame_right = np.zeros_like(frame_right_shifted)
            if bottom_shift > 0:
                shifted_frame_right[bottom_shift:, :] = frame_right_shifted[:-bottom_shift, :]
            else:
                shifted_frame_right[:bottom_shift, :] = frame_right_shifted[-bottom_shift:, :]
            frame_right_shifted = shifted_frame_right

        # Alpha blending
        left_region = frame_left[:, -overlap_width:]  # Right part of the left video
        right_region = frame_right_shifted[:, :overlap_width]  # Left part of the right video

        blended_region = cv2.addWeighted(left_region, 0.5, right_region, 0.5, 0)

        # Apply blended region to the frames
        frame_left[:, -overlap_width:] = blended_region
        frame_right_shifted[:, :overlap_width] = blended_region

        # Apply Gaussian blur to the overlap region
        blur_radius = 15  # Adjust blur strength
        overlap_blurred = cv2.GaussianBlur(frame_left[:, -overlap_width:], (blur_radius, blur_radius), 0)
        frame_left[:, -overlap_width:] = overlap_blurred

        # Concatenate the frames horizontally
        combined_frame = np.hstack((frame_left[:, :-overlap_width], frame_right_shifted[:, overlap_width:]))

        # Resize combined frame
        combined_frame_resized = cv2.resize(combined_frame, (target_width, target_height))

        # Write frame to the output video
        out.write(combined_frame_resized)

        # Display the combined frame
        cv2.imshow('Combined Video', combined_frame_resized)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources and finalize the output
    left_cap.release()
    right_cap.release()
    out.release()
    cv2.destroyAllWindows()

    print(f'Combined video saved as {output_path}')

# Create GUI components
label = tk.Label(window, text="Select Left and Right Videos", font=("Arial", 14))
label.pack(pady=20)

# Buttons to load videos
left_button = tk.Button(window, text="Load Left Video", command=load_left_video)
left_button.pack(pady=10)

right_button = tk.Button(window, text="Load Right Video", command=load_right_video)
right_button.pack(pady=10)

# Labels to show loaded video filenames
left_video_label = tk.Label(window, text="Left Video: Not Loaded", font=("Arial", 10))
left_video_label.pack()

right_video_label = tk.Label(window, text="Right Video: Not Loaded", font=("Arial", 10))
right_video_label.pack()

# Frame display labels
left_frame_label = tk.Label(window)
left_frame_label.pack(side="left", padx=20)

right_frame_label = tk.Label(window)
right_frame_label.pack(side="right", padx=20)

# Buttons for frame navigation
advance_left_button = tk.Button(window, text="Advance Left Frame", command=advance_left)
advance_left_button.pack(pady=10)

reverse_left_button = tk.Button(window, text="Reverse Left Frame", command=reverse_left)
reverse_left_button.pack(pady=10)

advance_right_button = tk.Button(window, text="Advance Right Frame", command=advance_right)
advance_right_button.pack(pady=10)

reverse_right_button = tk.Button(window, text="Reverse Right Frame", command=reverse_right)
reverse_right_button.pack(pady=10)

# Button to process and combine videos
stitch_button = tk.Button(window, text="Stitch and Process Videos", command=process_and_combine)
stitch_button.pack(pady=20)

# Run the Tkinter loop
window.mainloop()
