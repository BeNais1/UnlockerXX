import os
import sys
import psutil
import ctypes
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class FileUnlockerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python File Unlocker")
        self.root.geometry("600x400")

        # Make the app look a bit better
        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.create_widgets()

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # File selection
        file_frame = ttk.LabelFrame(main_frame, text="File/Folder to Unlock", padding="10")
        file_frame.pack(fill=tk.X, pady=5)

        self.file_path = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_path).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(file_frame, text="Browse...", command=self.browse_file).pack(side=tk.LEFT)

        # Actions frame
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=5)

        ttk.Button(action_frame, text="Unlock File", command=self.unlock_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="Delete File", command=self.delete_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="Kill Process", command=self.kill_process).pack(side=tk.LEFT, padx=2)

        # Process list
        process_frame = ttk.LabelFrame(main_frame, text="Locking Processes", padding="10")
        process_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(process_frame, columns=('pid', 'name', 'status'), show='headings')
        self.tree.heading('pid', text='PID')
        self.tree.heading('name', text='Process Name')
        self.tree.heading('status', text='Status')

        vsb = ttk.Scrollbar(process_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(process_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        process_frame.grid_rowconfigure(0, weight=1)
        process_frame.grid_columnconfigure(0, weight=1)

    def browse_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.file_path.set(file_path)
            self.find_locking_processes()

    def find_locking_processes(self):
        file_path = self.file_path.get()
        if not file_path or not os.path.exists(file_path):
            return

        self.tree.delete(*self.tree.get_children())

        try:
            for proc in psutil.process_iter(['pid', 'name', 'status']):
                try:
                    files = proc.open_files()
                    for f in files:
                        if os.path.normcase(f.path) == os.path.normcase(file_path):
                            self.tree.insert('', 'end',
                                             values=(proc.info['pid'], proc.info['name'], proc.info['status']))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            messagebox.showerror("Error", f"Failed to check processes: {str(e)}")

    def unlock_file(self):
        file_path = self.file_path.get()
        if not file_path:
            messagebox.showwarning("Warning", "Please select a file first")
            return

        try:
            # Try to open the file in read-write mode to "unlock" it
            with open(file_path, 'a'):
                os.utime(file_path, None)
            messagebox.showinfo("Success", "File unlocked successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to unlock file: {str(e)}")

    def delete_file(self):
        file_path = self.file_path.get()
        if not file_path:
            messagebox.showwarning("Warning", "Please select a file first")
            return

        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                os.rmdir(file_path)
            messagebox.showinfo("Success", "File/folder deleted successfully")
            self.file_path.set("")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete: {str(e)}")

    def kill_process(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a process first")
            return

        pid = self.tree.item(selected_item)['values'][0]
        try:
            p = psutil.Process(pid)
            p.terminate()
            messagebox.showinfo("Success", f"Process {pid} terminated")
            self.find_locking_processes()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to kill process: {str(e)}")


if __name__ == "__main__":
    # Check for admin rights (required for some operations)
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

    root = tk.Tk()
    app = FileUnlockerApp(root)
    root.mainloop()