import psutil
from tkinter import messagebox

def find_high_usage_processes(tree):
    tree.delete(*tree.get_children())
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                cpu = proc.info['cpu_percent']
                memory = proc.info['memory_percent']
                if cpu > 50 or memory > 50:
                    tree.insert('', 'end',
                                values=(proc.info['pid'], proc.info['name'], f"{cpu:.2f}", f"{memory:.2f}"))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as e:
        messagebox.showerror("Error", f"Failed to retrieve high usage processes: {str(e)}")

def kill_process(tree):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Warning", "Please select a process first")
        return
    pid = tree.item(selected_item)['values'][0]
    try:
        p = psutil.Process(pid)
        p.terminate()
        messagebox.showinfo("Success", f"Process {pid} terminated")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to kill process: {str(e)}")