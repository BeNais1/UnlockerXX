import os
import psutil
from tkinter import filedialog, messagebox

def browse_file(file_path_var, find_locking_processes):
    file_path = filedialog.askopenfilename()
    if file_path:
        file_path_var.set(file_path)
        find_locking_processes()

def find_locking_processes(file_path, tree):
    if not file_path or not os.path.exists(file_path):
        return
    tree.delete(*tree.get_children())
    try:
        for proc in psutil.process_iter(['pid', 'name', 'status']):
            try:
                files = proc.open_files()
                for f in files:
                    if os.path.normcase(f.path) == os.path.normcase(file_path):
                        tree.insert('', 'end',
                                    values=(proc.info['pid'], proc.info['name'], proc.info['status']))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as e:
        messagebox.showerror("Error", f"Failed to check processes: {str(e)}")

def unlock_file(file_path):
    if not file_path:
        messagebox.showwarning("Warning", "Please select a file first")
        return
    try:
        with open(file_path, 'a'):
            os.utime(file_path, None)
        messagebox.showinfo("Success", "File unlocked successfully")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to unlock file: {str(e)}")

def delete_file(file_path):
    if not file_path:
        messagebox.showwarning("Warning", "Please select a file first")
        return
    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            os.rmdir(file_path)
        messagebox.showinfo("Success", "File/folder deleted successfully")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to delete: {str(e)}")