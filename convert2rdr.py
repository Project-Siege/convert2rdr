import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import shutil
import os
import tempfile

def check_redm_folder():
    global redm_path
    redm_path = os.path.join(os.getenv('LOCALAPPDATA'), 'RedM', 'RedM.app')
    if not os.path.exists(redm_path):
        messagebox.showerror("Error", "RedM folder not found in AppData\\Local")
        select_redm_directory()
    else:
        enable_buttons()

def select_redm_directory():
    global redm_path
    redm_path = filedialog.askdirectory(title='Select RedM Directory')
    if redm_path:
        enable_buttons()

def enable_buttons():
    select_button.config(state=tk.NORMAL)
    send_to_button.config(state=tk.NORMAL)
    convert_button.config(state=tk.NORMAL)

def select_files():
    filetypes = [('YDR and YBN files', '*.ydr *.ybn')]
    filenames = filedialog.askopenfilenames(title='Select files', filetypes=filetypes)
    listbox.delete(0, tk.END)
    for filename in filenames:
        listbox.insert(tk.END, filename)
    check_convert_button_state()

def select_output_folder():
    global output_folder
    output_folder = filedialog.askdirectory(title='Select output folder')
    if output_folder:
        output_label.config(text=f"Output Folder: {output_folder}")
    check_convert_button_state()

def convert_files():
    files = listbox.get(0, tk.END)
    if not files or not output_folder:
        messagebox.showerror("Error", "No files selected or output folder not set")
        return

    temp_dir = tempfile.mkdtemp()  # Create a temporary directory
    copied_files = []
    try:
        # Copy files to the temporary directory
        for file in files:
            shutil.copy(file, temp_dir)
            copied_files.append(os.path.join(temp_dir, os.path.basename(file)))

        os.chdir(redm_path)  # Change working directory to RedM folder
        command = 'CitiCon.com formats:convert'
        file_string = " ".join(copied_files)
        subprocess.run(f'{command} {file_string}', shell=True, check=True)

        # Move and rename the converted files
        for file in copied_files:
            base, ext = os.path.splitext(file)
            new_file = f"{base}_nya{ext}"
            final_file_name = f"{os.path.splitext(os.path.basename(file))[0]}{ext}"  # Remove _nya from the final file name
            destination_file = os.path.join(output_folder, final_file_name)
            if os.path.exists(destination_file):
                os.remove(destination_file)
            shutil.move(new_file, destination_file)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        shutil.rmtree(temp_dir)  # Clean up the temporary directory
    messagebox.showinfo("Success", "Conversion and moving completed successfully")

def check_convert_button_state():
    if listbox.size() > 0 and output_folder:
        convert_button.config(state=tk.NORMAL)
    else:
        convert_button.config(state=tk.DISABLED)

root = tk.Tk()
root.title("Convert2RDR")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

listbox = tk.Listbox(frame, width=50, height=15)
listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(frame, orient="vertical")
scrollbar.config(command=listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

listbox.config(yscrollcommand=scrollbar.set)

output_folder = None
output_label = tk.Label(root, text="Output Folder: Not set")
output_label.pack(pady=5)

btn_frame = tk.Frame(root)
btn_frame.pack(padx=10, pady=10)

select_button = tk.Button(btn_frame, text="Select Files", command=select_files, state=tk.DISABLED)
select_button.pack(side=tk.LEFT, padx=5)

send_to_button = tk.Button(btn_frame, text="Send To", command=select_output_folder, state=tk.DISABLED)
send_to_button.pack(side=tk.LEFT, padx=5)

convert_button = tk.Button(btn_frame, text="Convert", command=convert_files, state=tk.DISABLED)
convert_button.pack(side=tk.LEFT, padx=5)

check_redm_folder()

root.mainloop()